"""
Flask app for the booklet production pipeline.

Browse parsed lessons, filter by subject/year/topic, view lesson details,
generate booklets via Claude API, validate, and upload to Google Drive.

Supports multiple courses via scheme-of-work upload.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from threading import Lock

from flask import Flask, Response, render_template, request, jsonify
from prompt_generator import generate_master_prompt
import courses
import tracker

app = Flask(__name__)

# Logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Directory for uploaded spreadsheets
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Parsed data cache: { course_id: parsed_data_dict }
_course_data = {}

# Current active course
_active_course_id = courses.get_default_course_id()


def get_data(course_id=None):
    """Get parsed data for a course, loading/parsing on first access."""
    global _active_course_id
    cid = course_id or _active_course_id

    if cid not in _course_data:
        config = courses.get_course(cid)
        if not config:
            raise ValueError(f"Course not found: {cid}")

        # Use the generic parser for all courses
        from generic_parser import parse_course
        _course_data[cid] = parse_course(config)

    return _course_data[cid]


def get_active_course_config():
    """Get the full config for the currently active course."""
    return courses.get_course(_active_course_id)


# --- Batch generation state ---
_batch_state = {}
_batch_lock = Lock()


# ========================================================================
# Pages
# ========================================================================

@app.route("/")
def index():
    data = get_data()
    stats = data["stats"]
    subjects = sorted(set(
        l["subject"] for l in data["booklet_lessons"] if l["subject"]
    ))
    topics = sorted(set(
        l["topic"] for l in data["booklet_lessons"] if l["topic"]
    ))
    years = sorted(set(
        l["year"] for l in data["booklet_lessons"]
    ))
    course_list = courses.list_courses()
    active_config = get_active_course_config()
    return render_template(
        "index.html",
        stats=stats,
        subjects=subjects,
        topics=topics,
        years=years,
        courses=course_list,
        active_course=active_config,
    )


# ========================================================================
# Course management API
# ========================================================================

@app.route("/api/courses")
def api_courses():
    return jsonify({
        "courses": courses.list_courses(),
        "active": _active_course_id,
    })


@app.route("/api/courses/switch", methods=["POST"])
def api_switch_course():
    global _active_course_id
    body = request.get_json() or {}
    course_id = body.get("course_id")
    if not course_id:
        return jsonify({"error": "course_id required"}), 400

    config = courses.get_course(course_id)
    if not config:
        return jsonify({"error": "Course not found"}), 404

    _active_course_id = course_id
    # Force re-parse on next access
    _course_data.pop(course_id, None)

    return jsonify({"active": course_id, "name": config["name"]})


@app.route("/api/courses/<course_id>")
def api_get_course(course_id):
    config = courses.get_course(course_id)
    if not config:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(config)


@app.route("/api/courses/<course_id>", methods=["DELETE"])
def api_delete_course(course_id):
    try:
        courses.delete_course(course_id)
        _course_data.pop(course_id, None)
        return jsonify({"deleted": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/courses/upload", methods=["POST"])
def api_upload_spreadsheet():
    """Upload a scheme of work spreadsheet and preview its structure."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "Only .xlsx or .xls files are supported"}), 400

    # Save the uploaded file
    safe_name = file.filename.replace(" ", "_")
    save_path = UPLOADS_DIR / safe_name
    file.save(str(save_path))

    # Preview the spreadsheet
    from generic_parser import preview_spreadsheet
    try:
        preview = preview_spreadsheet(str(save_path))
    except Exception as e:
        return jsonify({"error": f"Could not read spreadsheet: {e}"}), 400

    return jsonify({
        "filename": safe_name,
        "path": str(save_path),
        "preview": preview,
    })


@app.route("/api/courses/preview", methods=["POST"])
def api_preview_spreadsheet():
    """Preview an already-uploaded spreadsheet (or re-preview with different settings)."""
    body = request.get_json() or {}
    xlsx_path = body.get("xlsx_path")
    if not xlsx_path:
        return jsonify({"error": "xlsx_path required"}), 400

    from generic_parser import preview_spreadsheet
    try:
        preview = preview_spreadsheet(xlsx_path)
    except Exception as e:
        return jsonify({"error": f"Could not read spreadsheet: {e}"}), 400

    return jsonify({"preview": preview})


@app.route("/api/courses/save", methods=["POST"])
def api_save_course():
    """Save a new course configuration after the user has mapped columns."""
    body = request.get_json() or {}

    required = ["name", "xlsx_path", "sheets", "col_map"]
    for field in required:
        if field not in body:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    config = {
        "name": body["name"],
        "exam_board": body.get("exam_board", ""),
        "qualification": body.get("qualification", ""),
        "key_stage": body.get("key_stage", ""),
        "subjects": body.get("subjects", []),
        "xlsx_path": body["xlsx_path"],
        "sheets": body["sheets"],
        "header_row": body.get("header_row", 1),
        "col_map": body["col_map"],
        "topic_folders": body.get("topic_folders", {}),
        "subject_from_topic_prefix": body.get("subject_from_topic_prefix", {}),
        "topic_code_pattern": body.get("topic_code_pattern", ""),
        "fixed_subject": body.get("fixed_subject"),
        "system_prompt_context": body.get("system_prompt_context", body["name"]),
        "prior_knowledge_base": body.get(
            "prior_knowledge_base",
            f"Students have completed the relevant prior learning for this course."
        ),
    }

    # If editing an existing course, keep its ID
    if body.get("id"):
        config["id"] = body["id"]

    saved = courses.save_course(config)

    # Clear cache so it re-parses
    _course_data.pop(saved["id"], None)

    return jsonify({"saved": True, "course": saved})


# ========================================================================
# Update Scheme of Work API
# ========================================================================

@app.route("/api/courses/<course_id>/update-scheme", methods=["POST"])
def api_update_scheme_preview(course_id):
    """Upload a new spreadsheet and preview what will change (non-destructive)."""
    config = courses.get_course(course_id)
    if not config:
        return jsonify({"error": "Course not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "Only .xlsx or .xls files supported"}), 400

    safe_name = file.filename.replace(" ", "_")
    save_path = UPLOADS_DIR / safe_name
    file.save(str(save_path))

    from generic_parser import parse_course, compare_schemes
    import openpyxl

    new_config = dict(config)
    new_config["xlsx_path"] = str(save_path)

    # ── Auto-remap sheet names if they changed ──
    try:
        wb = openpyxl.load_workbook(str(save_path), read_only=True)
        actual_sheets = wb.sheetnames
        wb.close()
    except Exception as e:
        return jsonify({"error": f"Could not open spreadsheet: {e}"}), 400

    sheet_remap = {}
    new_sheets = list(new_config.get("sheets", []))
    for i, sheet_info in enumerate(new_sheets):
        old_name = sheet_info["name"]
        if old_name in actual_sheets:
            continue  # exact match, no remap needed
        year = sheet_info["year"]
        # Try fuzzy match: find a sheet containing the year number
        # and a keyword like "lesson" (case-insensitive)
        candidates = []
        for sn in actual_sheets:
            sn_lower = sn.lower().replace("_", " ")
            if str(year) in sn and "lesson" in sn_lower:
                candidates.append(sn)
        if len(candidates) == 1:
            sheet_remap[old_name] = candidates[0]
            new_sheets[i] = {**sheet_info, "name": candidates[0]}
        elif not candidates:
            # Broader match: just contains the year number
            for sn in actual_sheets:
                if str(year) in sn and sn not in [s["name"] for s in new_sheets[:i]]:
                    candidates.append(sn)
            if len(candidates) == 1:
                sheet_remap[old_name] = candidates[0]
                new_sheets[i] = {**sheet_info, "name": candidates[0]}

    new_config["sheets"] = new_sheets

    # ── Auto-detect column changes ──
    # Check if header row columns shifted by comparing expected headers
    col_warnings = []
    for sheet_info in new_sheets:
        sn = sheet_info["name"]
        if sn not in actual_sheets:
            continue
        try:
            wb2 = openpyxl.load_workbook(str(save_path), read_only=True)
            ws = wb2[sn]
            header_row_idx = new_config.get("header_row", 1)
            for ri, row in enumerate(ws.iter_rows(max_row=header_row_idx + 1, values_only=True), 1):
                if ri == header_row_idx + 1:
                    headers = [str(c).strip().lower() if c else "" for c in row]
            wb2.close()

            col_map = new_config.get("col_map", {})
            # Check that key columns still look right
            for field, idx in col_map.items():
                if idx < len(headers):
                    h = headers[idx]
                    # Basic sanity: if 'topic' column now says 'disciplinary' or 'progression', flag it
                    if field == "topic" and ("disciplin" in h or "progression" in h):
                        # Try to find the actual topic/substantive column
                        for ni, nh in enumerate(headers):
                            if "substantive" in nh or "concept" in nh and "second" not in nh:
                                col_warnings.append(f"Column '{field}' remapped from {idx} to {ni} (was '{headers[idx]}', now '{nh}')")
                                new_config.setdefault("col_map", {})[field] = ni
                                break
        except Exception:
            pass

    try:
        new_data = parse_course(new_config)
    except Exception as e:
        return jsonify({"error": f"Could not parse spreadsheet: {e}"}), 400

    try:
        old_data = get_data(course_id)
    except Exception:
        old_data = {"booklet_lessons": [], "all_lessons": []}

    diff = compare_schemes(
        old_data["booklet_lessons"],
        new_data["booklet_lessons"]
    )

    return jsonify({
        "new_xlsx_path": str(save_path),
        "diff": {
            "summary": diff["summary"],
            "modified": [
                {
                    "year": m["key"][0],
                    "lesson_number": m["key"][1],
                    "old_title": m["old"].get("title", ""),
                    "new_title": m["new"].get("title", ""),
                }
                for m in diff["modified"]
            ],
            "added": [
                {
                    "year": a["key"][0],
                    "lesson_number": a["key"][1],
                    "title": a["new"].get("title", ""),
                }
                for a in diff["added"]
            ],
            "removed": [
                {
                    "year": r["key"][0],
                    "lesson_number": r["key"][1],
                    "title": r["old"].get("title", ""),
                }
                for r in diff["removed"]
            ],
        },
        "new_stats": new_data["stats"],
        "sheet_remap": sheet_remap,
        "col_remap": {k: v for k, v in new_config.get("col_map", {}).items()},
        "col_warnings": col_warnings,
        "new_sheets": new_sheets,
    })


@app.route("/api/courses/<course_id>/apply-update", methods=["POST"])
def api_apply_scheme_update(course_id):
    """Apply a previously previewed scheme update (destructive, user-confirmed)."""
    config = courses.get_course(course_id)
    if not config:
        return jsonify({"error": "Course not found"}), 404

    body = request.get_json() or {}
    new_xlsx_path = body.get("new_xlsx_path")
    delete_removed = body.get("delete_removed", True)
    reset_modified = body.get("reset_modified", True)
    delete_from_drive = body.get("delete_from_drive", False)
    new_sheets = body.get("new_sheets")  # remapped sheet names from preview
    col_remap = body.get("col_remap")    # remapped column indices from preview

    if not new_xlsx_path:
        return jsonify({"error": "new_xlsx_path required"}), 400

    from generic_parser import parse_course, compare_schemes
    from generator import delete_lesson_files_from_disk

    try:
        old_data = get_data(course_id)
    except Exception:
        old_data = {"booklet_lessons": [], "all_lessons": []}

    new_config = dict(config)
    new_config["xlsx_path"] = new_xlsx_path
    if new_sheets:
        new_config["sheets"] = new_sheets
    if col_remap:
        # col_remap values come as strings from JSON; convert to int
        new_config["col_map"] = {k: int(v) for k, v in col_remap.items()}
    new_data = parse_course(new_config)

    diff = compare_schemes(
        old_data["booklet_lessons"],
        new_data["booklet_lessons"]
    )

    results = {
        "disk_deleted": [],
        "drive_deleted": [],
        "progress_cleared": [],
        "errors": [],
    }

    # Handle removed lessons
    if delete_removed and diff["removed"]:
        for item in diff["removed"]:
            lesson = item["old"]
            try:
                disk_result = delete_lesson_files_from_disk(lesson)
                results["disk_deleted"].extend(disk_result["deleted"])
            except Exception as e:
                results["errors"].append(
                    f"Disk delete failed for Y{lesson['year']}_L{lesson['lesson_number']}: {e}"
                )

            if delete_from_drive:
                try:
                    from gdrive import delete_lesson_files_from_drive
                    drive_folder = config.get("gdrive_folder_id") or None
                    drive_result = delete_lesson_files_from_drive(
                        lesson, root_folder_id=drive_folder
                    )
                    results["drive_deleted"].extend(drive_result["deleted"])
                    results["errors"].extend(drive_result["errors"])
                except Exception as e:
                    results["errors"].append(
                        f"Drive delete failed for Y{lesson['year']}_L{lesson['lesson_number']}: {e}"
                    )

        removed_keys = [
            (item["old"]["year"], item["old"]["lesson_number"])
            for item in diff["removed"]
        ]
        tracker.clear_lessons(removed_keys, course_id)
        results["progress_cleared"].extend(
            [f"Y{y}_L{n:03d}" for y, n in removed_keys]
        )

    # Handle modified lessons — reset progress so they get regenerated
    if reset_modified and diff["modified"]:
        modified_keys = [(m["key"][0], m["key"][1]) for m in diff["modified"]]
        tracker.clear_lessons(modified_keys, course_id)
        results["progress_cleared"].extend(
            [f"Y{y}_L{n:03d}" for y, n in modified_keys]
        )

    # Update course config with new spreadsheet path, sheets, and col_map
    config["xlsx_path"] = new_xlsx_path
    if new_sheets:
        config["sheets"] = new_sheets
    if col_remap:
        config["col_map"] = {k: int(v) for k, v in col_remap.items()}
    courses.save_course(config)

    # Clear cache to force re-parse
    _course_data.pop(course_id, None)

    try:
        get_data(course_id)
    except Exception as e:
        results["errors"].append(f"Re-parse failed: {e}")

    return jsonify({
        "success": True,
        "results": results,
        "diff_summary": diff["summary"],
    })


# ========================================================================
# Lessons API
# ========================================================================

@app.route("/api/lessons")
def api_lessons():
    data = get_data()
    lessons = data["booklet_lessons"]

    subject = request.args.get("subject")
    year = request.args.get("year")
    topic = request.args.get("topic")
    search = request.args.get("search", "").strip().lower()

    if subject:
        lessons = [l for l in lessons if l["subject"] == subject]
    if year:
        lessons = [l for l in lessons if str(l["year"]) == year]
    if topic:
        lessons = [l for l in lessons if l["topic"] == topic]
    if search:
        lessons = [
            l for l in lessons
            if search in (l["title"] or "").lower()
            or search in (l["spec_content"] or "").lower()
            or search in (l["key_vocabulary"] or "").lower()
        ]

    status_filter = request.args.get("status")
    if status_filter:
        statuses = tracker.get_all_statuses(_active_course_id)
        lessons = [
            l for l in lessons
            if statuses.get(tracker._key(l['year'], l['lesson_number'], _active_course_id), "pending") == status_filter
        ]

    statuses = tracker.get_all_statuses(_active_course_id)
    for l in lessons:
        l["status"] = statuses.get(tracker._key(l['year'], l['lesson_number'], _active_course_id), "pending")

    return jsonify(lessons)


@app.route("/api/lesson/<int:year>/<int:lesson_num>")
def api_lesson_detail(year, lesson_num):
    data = get_data()
    for l in data["all_lessons"]:
        if l["year"] == year and l["lesson_number"] == lesson_num:
            return jsonify(l)
    return jsonify({"error": "Lesson not found"}), 404


@app.route("/api/prompt/<int:year>/<int:lesson_num>")
def api_prompt(year, lesson_num):
    data = get_data()
    for l in data["booklet_lessons"]:
        if l["year"] == year and l["lesson_number"] == lesson_num:
            config = get_active_course_config()
            prompt = generate_master_prompt(l, course_config=config)
            return jsonify({"prompt": prompt, "lesson": l})
    return jsonify({"error": "Lesson not found"}), 404


@app.route("/api/filtered-out")
def api_filtered_out():
    data = get_data()
    non_booklet = [l for l in data["all_lessons"] if not l["is_booklet_lesson"]]
    return jsonify(non_booklet)


@app.route("/api/reload", methods=["POST"])
def api_reload():
    global _course_data
    _course_data.pop(_active_course_id, None)
    get_data()
    return jsonify({"status": "ok", "stats": get_data()["stats"]})


# ========================================================================
# Progress tracking
# ========================================================================

@app.route("/api/status/<int:year>/<int:lesson_num>")
def api_get_status(year, lesson_num):
    return jsonify({"status": tracker.get_status(year, lesson_num, _active_course_id)})


@app.route("/api/status/<int:year>/<int:lesson_num>", methods=["POST"])
def api_set_status(year, lesson_num):
    body = request.get_json()
    status = body.get("status", "pending")
    try:
        tracker.set_status(year, lesson_num, status, _active_course_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": status})


@app.route("/api/statuses")
def api_all_statuses():
    return jsonify(tracker.get_all_statuses(_active_course_id))


@app.route("/api/progress-summary")
def api_progress_summary():
    data = get_data()
    return jsonify(tracker.get_summary(data["booklet_lessons"], _active_course_id))


# ========================================================================
# Batch export (prompts to .txt)
# ========================================================================

EXPORT_DIR = Path(__file__).parent / "prompts"


@app.route("/api/export", methods=["POST"])
def api_export_prompts():
    data = get_data()
    lessons = data["booklet_lessons"]
    config = get_active_course_config()

    body = request.get_json() or {}
    subject = body.get("subject")
    year = body.get("year")
    status_filter = body.get("status")

    if subject:
        lessons = [l for l in lessons if l["subject"] == subject]
    if year:
        lessons = [l for l in lessons if str(l["year"]) == str(year)]
    if status_filter:
        statuses = tracker.get_all_statuses(_active_course_id)
        lessons = [
            l for l in lessons
            if statuses.get(tracker._key(l['year'], l['lesson_number'], _active_course_id), "pending") == status_filter
        ]

    EXPORT_DIR.mkdir(exist_ok=True)
    exported = []
    for l in lessons:
        prompt = generate_master_prompt(l, course_config=config)
        subdir = EXPORT_DIR / (l["subject"] or "Unknown")
        subdir.mkdir(exist_ok=True)
        fname = f"L{l['lesson_number']:03d} - {l['title']}.txt"
        fname = fname.replace("/", "-").replace(":", " -")
        fpath = subdir / fname
        fpath.write_text(prompt)
        exported.append(str(fpath.relative_to(EXPORT_DIR)))

    return jsonify({
        "exported": len(exported),
        "directory": str(EXPORT_DIR),
        "files": exported,
    })


# ========================================================================
# Check if booklet exists
# ========================================================================

@app.route("/api/check-exists/<int:year>/<int:lesson_num>")
def api_check_exists(year, lesson_num):
    from generator import check_existing_booklet

    data = get_data()
    lesson = _find_lesson(data, year, lesson_num)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    result = check_existing_booklet(lesson)
    return jsonify(result)


# ========================================================================
# Generate via Claude API
# ========================================================================

@app.route("/api/generate/<int:year>/<int:lesson_num>", methods=["POST"])
def api_generate(year, lesson_num):
    from generator import generate_and_save

    data = get_data()
    lesson = _find_lesson(data, year, lesson_num)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    body = request.get_json() or {}
    model = body.get("model", "claude-sonnet-4-5-20250929")
    replace = body.get("replace", False)

    config = get_active_course_config()
    prompt = generate_master_prompt(lesson, course_config=config)

    try:
        result = generate_and_save(
            lesson, prompt, model=model, replace=replace,
            course_config=config,
        )

        if replace:
            logger.info(
                f"REPLACED booklet Y{year}_L{lesson_num:03d} "
                f"'{lesson['title']}' at {datetime.now().isoformat()}"
            )

        tracker.set_status(year, lesson_num, "generated", _active_course_id)
        return jsonify({
            "success": True,
            "md_path": result["md_path"],
            "docx_path": result["docx_path"],
            "pdf_path": result.get("pdf_path"),
            "usage": result["usage"],
            "model": result["model"],
            "duration_s": result["duration_s"],
        })
    except FileExistsError as e:
        return jsonify({
            "error": str(e),
            "exists": True,
        }), 409
    except Exception as e:
        logger.error(f"Generate failed for Y{year}_L{lesson_num:03d}: {e}")
        return jsonify({"error": str(e)}), 500


# ========================================================================
# Generate All — SSE stream
# ========================================================================

@app.route("/api/generate-all", methods=["POST"])
def api_generate_all():
    from generator import generate_and_save, check_existing_booklet

    data = get_data()
    body = request.get_json() or {}

    subject = body.get("subject")
    year = body.get("year")
    replace_all = body.get("replace_all", False)
    model = body.get("model", "claude-sonnet-4-5-20250929")

    config = get_active_course_config()

    lesson_ids = body.get("lesson_ids")  # e.g. ["Y7_L001", "Y8_L005"] for custom selection

    lessons = list(data["booklet_lessons"])
    if subject:
        lessons = [l for l in lessons if l["subject"] == subject]
    if year:
        lessons = [l for l in lessons if str(l["year"]) == str(year)]

    # Custom lesson selection overrides subject/year filter
    if lesson_ids:
        id_set = set(lesson_ids)
        lessons = [l for l in lessons if f"Y{l['year']}_L{l['lesson_number']:03d}" in id_set]

    # Only generate pending lessons unless replace_all
    if not replace_all:
        statuses = tracker.get_all_statuses(_active_course_id)
        lessons = [
            l for l in lessons
            if statuses.get(tracker._key(l['year'], l['lesson_number'], _active_course_id), "pending") == "pending"
        ]

    batch_id = str(uuid.uuid4())[:8]
    with _batch_lock:
        _batch_state[batch_id] = {"cancelled": False}

    def generate_stream():
        total = len(lessons)
        generated = 0
        replaced = 0
        skipped = 0
        errors = 0

        yield f"data: {json.dumps({'type': 'start', 'batch_id': batch_id, 'total': total})}\n\n"

        for idx, lesson in enumerate(lessons):
            # Check cancellation
            with _batch_lock:
                if _batch_state.get(batch_id, {}).get("cancelled"):
                    yield f"data: {json.dumps({'type': 'cancelled', 'current': idx, 'total': total})}\n\n"
                    break

            y = lesson["year"]
            ln = lesson["lesson_number"]
            title = lesson["title"]

            yield f"data: {json.dumps({'type': 'progress', 'current': idx + 1, 'total': total, 'title': title, 'year': y, 'lesson_num': ln})}\n\n"

            try:
                existing = check_existing_booklet(lesson)
                is_replace = existing["exists"]

                if is_replace and not replace_all:
                    skipped += 1
                    yield f"data: {json.dumps({'type': 'skipped', 'title': title, 'reason': 'exists'})}\n\n"
                    continue

                prompt = generate_master_prompt(lesson, course_config=config)
                result = generate_and_save(
                    lesson, prompt, model=model, replace=True,
                    course_config=config,
                )
                tracker.set_status(y, ln, "generated", _active_course_id)

                if is_replace:
                    replaced += 1
                    logger.info(
                        f"BATCH REPLACED Y{y}_L{ln:03d} '{title}' "
                        f"at {datetime.now().isoformat()}"
                    )
                else:
                    generated += 1

                yield f"data: {json.dumps({'type': 'done', 'title': title, 'replaced': is_replace, 'duration_s': result['duration_s'], 'usage': result['usage'], 'model': result['model']})}\n\n"

            except Exception as e:
                errors += 1
                logger.error(f"Batch generate failed for Y{y}_L{ln:03d}: {e}")
                yield f"data: {json.dumps({'type': 'error', 'title': title, 'error': str(e)})}\n\n"

        summary = {
            "type": "complete",
            "generated": generated,
            "replaced": replaced,
            "skipped": skipped,
            "errors": errors,
            "total": total,
        }
        yield f"data: {json.dumps(summary)}\n\n"

        # Cleanup batch state
        with _batch_lock:
            _batch_state.pop(batch_id, None)

    return Response(
        generate_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/generate-all/cancel", methods=["POST"])
def api_cancel_batch():
    body = request.get_json() or {}
    batch_id = body.get("batch_id")

    if not batch_id:
        # Cancel all batches
        with _batch_lock:
            for bid in _batch_state:
                _batch_state[bid]["cancelled"] = True
        return jsonify({"cancelled": True})

    with _batch_lock:
        if batch_id in _batch_state:
            _batch_state[batch_id]["cancelled"] = True
            return jsonify({"cancelled": True})

    return jsonify({"error": "Batch not found"}), 404


# ========================================================================
# Reprocess existing booklets — re-sanitise markdown + rebuild docx/pdf
# ========================================================================

@app.route("/api/reprocess-all", methods=["POST"])
def api_reprocess_all():
    """
    Re-sanitise every .md file in the output directory and rebuild its
    .docx and .pdf.  Used to apply numbering/formatting fixes to booklets
    that were generated with an older version of the pipeline.
    """
    from generator import sanitize_markdown, markdown_to_docx, convert_to_pdf, OUTPUT_DIR

    def stream():
        md_files = sorted(Path(OUTPUT_DIR).rglob("*.md"))
        total = len(md_files)
        yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"

        done = errors = 0
        for i, md_path in enumerate(md_files):
            try:
                content = md_path.read_text(encoding="utf-8")
                clean = sanitize_markdown(content)
                md_path.write_text(clean, encoding="utf-8")

                docx_path = markdown_to_docx(str(md_path))
                convert_to_pdf(docx_path)

                done += 1
                yield f"data: {json.dumps({'type': 'progress', 'current': i + 1, 'total': total, 'file': md_path.name})}\n\n"
            except Exception as e:
                errors += 1
                logger.error(f"Reprocess failed for {md_path.name}: {e}")
                yield f"data: {json.dumps({'type': 'error', 'file': md_path.name, 'error': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'complete', 'done': done, 'errors': errors, 'total': total})}\n\n"

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ========================================================================
# Validate .docx
# ========================================================================

@app.route("/api/validate/<int:year>/<int:lesson_num>", methods=["POST"])
def api_validate(year, lesson_num):
    from validator import validate_docx
    from generator import check_existing_booklet

    data = get_data()
    lesson = _find_lesson(data, year, lesson_num)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    existing = check_existing_booklet(lesson)
    if not existing["exists"]:
        return jsonify({"error": f"File not found: {existing['docx_path']}. Generate it first."}), 404

    docx_path = Path(existing["docx_path"])

    try:
        result = validate_docx(str(docx_path))
        if result["valid"]:
            tracker.set_status(year, lesson_num, "qa_passed", _active_course_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================================================================
# Google Drive upload
# ========================================================================

@app.route("/api/upload/<int:year>/<int:lesson_num>", methods=["POST"])
def api_upload(year, lesson_num):
    from gdrive import upload_booklet
    from generator import check_existing_booklet

    data = get_data()
    lesson = _find_lesson(data, year, lesson_num)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    existing = check_existing_booklet(lesson)
    if not existing["exists"]:
        return jsonify({"error": f"File not found: {existing['docx_path']}. Generate it first."}), 404

    docx_path = Path(existing["docx_path"])

    try:
        # Use per-course Drive folder if configured, otherwise global
        config = get_active_course_config()
        drive_folder = (config or {}).get("gdrive_folder_id") or None
        result = upload_booklet(str(docx_path), lesson, root_folder_id=drive_folder)
        tracker.set_status(year, lesson_num, "uploaded", _active_course_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/gdrive/check")
def api_gdrive_check():
    from gdrive import check_connection
    return jsonify(check_connection())


# ========================================================================
# Config / setup
# ========================================================================

@app.route("/api/config")
def api_config():
    from dotenv import load_dotenv
    load_dotenv()
    return jsonify({
        "anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "gdrive_folder": bool(os.getenv("GDRIVE_ROOT_FOLDER_ID")),
        "gdrive_secrets": Path(
            os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")
        ).exists() or (Path(__file__).parent / os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")).exists(),
        "gdrive_token": (Path(__file__).parent / "gdrive_token.json").exists(),
    })


@app.route("/api/env", methods=["GET"])
def api_env_read():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return jsonify({"exists": False, "content": ""})
    raw = env_path.read_text()
    return jsonify({"exists": True, "content": raw})


@app.route("/api/env", methods=["POST"])
def api_env_write():
    body = request.get_json() or {}
    content = body.get("content", "")
    env_path = Path(__file__).parent / ".env"
    env_path.write_text(content)
    from dotenv import load_dotenv
    load_dotenv(override=True)
    return jsonify({"saved": True})


# ========================================================================
# Helpers
# ========================================================================

def _find_lesson(data, year, lesson_num):
    """Find a booklet lesson by year and number."""
    for l in data["booklet_lessons"]:
        if l["year"] == year and l["lesson_number"] == lesson_num:
            return l
    return None


if __name__ == "__main__":
    app.run(debug=True, port=5050)
