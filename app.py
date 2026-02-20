"""
Flask app for the booklet production pipeline.

Browse parsed lessons, filter by subject/year/topic, view lesson details,
generate booklets via Claude API, validate, and upload to Google Drive.
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
from parser import parse_scheme_of_work
from prompt_generator import generate_master_prompt
import tracker

app = Flask(__name__)

# Logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

XLSX_PATH = "/Users/derek/Downloads/AQA_Combined_Science_Trilogy_Scheme_of_Work.xlsx"

# Parse once at startup
_data = None


def get_data():
    global _data
    if _data is None:
        _data = parse_scheme_of_work(XLSX_PATH)
    return _data


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
    return render_template(
        "index.html",
        stats=stats,
        subjects=subjects,
        topics=topics,
    )


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
        statuses = tracker.get_all_statuses()
        lessons = [
            l for l in lessons
            if statuses.get(f"Y{l['year']}_L{l['lesson_number']:03d}", "pending") == status_filter
        ]

    statuses = tracker.get_all_statuses()
    for l in lessons:
        l["status"] = statuses.get(f"Y{l['year']}_L{l['lesson_number']:03d}", "pending")

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
            prompt = generate_master_prompt(l)
            return jsonify({"prompt": prompt, "lesson": l})
    return jsonify({"error": "Lesson not found"}), 404


@app.route("/api/filtered-out")
def api_filtered_out():
    data = get_data()
    non_booklet = [l for l in data["all_lessons"] if not l["is_booklet_lesson"]]
    return jsonify(non_booklet)


@app.route("/api/reload", methods=["POST"])
def api_reload():
    global _data
    _data = None
    get_data()
    return jsonify({"status": "ok", "stats": get_data()["stats"]})


# ========================================================================
# Progress tracking
# ========================================================================

@app.route("/api/status/<int:year>/<int:lesson_num>")
def api_get_status(year, lesson_num):
    return jsonify({"status": tracker.get_status(year, lesson_num)})


@app.route("/api/status/<int:year>/<int:lesson_num>", methods=["POST"])
def api_set_status(year, lesson_num):
    body = request.get_json()
    status = body.get("status", "pending")
    try:
        tracker.set_status(year, lesson_num, status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": status})


@app.route("/api/statuses")
def api_all_statuses():
    return jsonify(tracker.get_all_statuses())


@app.route("/api/progress-summary")
def api_progress_summary():
    data = get_data()
    return jsonify(tracker.get_summary(data["booklet_lessons"]))


# ========================================================================
# Batch export (prompts to .txt)
# ========================================================================

EXPORT_DIR = Path(__file__).parent / "prompts"


@app.route("/api/export", methods=["POST"])
def api_export_prompts():
    data = get_data()
    lessons = data["booklet_lessons"]

    body = request.get_json() or {}
    subject = body.get("subject")
    year = body.get("year")
    status_filter = body.get("status")

    if subject:
        lessons = [l for l in lessons if l["subject"] == subject]
    if year:
        lessons = [l for l in lessons if str(l["year"]) == str(year)]
    if status_filter:
        statuses = tracker.get_all_statuses()
        lessons = [
            l for l in lessons
            if statuses.get(f"Y{l['year']}_L{l['lesson_number']:03d}", "pending") == status_filter
        ]

    EXPORT_DIR.mkdir(exist_ok=True)
    exported = []
    for l in lessons:
        prompt = generate_master_prompt(l)
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

    prompt = generate_master_prompt(lesson)

    try:
        result = generate_and_save(lesson, prompt, model=model, replace=replace)

        if replace:
            logger.info(
                f"REPLACED booklet Y{year}_L{lesson_num:03d} "
                f"'{lesson['title']}' at {datetime.now().isoformat()}"
            )

        tracker.set_status(year, lesson_num, "generated")
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

    lessons = list(data["booklet_lessons"])
    if subject:
        lessons = [l for l in lessons if l["subject"] == subject]
    if year:
        lessons = [l for l in lessons if str(l["year"]) == str(year)]

    # Only generate pending lessons unless replace_all
    if not replace_all:
        statuses = tracker.get_all_statuses()
        lessons = [
            l for l in lessons
            if statuses.get(f"Y{l['year']}_L{l['lesson_number']:03d}", "pending") == "pending"
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

                prompt = generate_master_prompt(lesson)
                result = generate_and_save(
                    lesson, prompt, model=model, replace=True
                )
                tracker.set_status(y, ln, "generated")

                if is_replace:
                    replaced += 1
                    logger.info(
                        f"BATCH REPLACED Y{y}_L{ln:03d} '{title}' "
                        f"at {datetime.now().isoformat()}"
                    )
                else:
                    generated += 1

                yield f"data: {json.dumps({'type': 'done', 'title': title, 'replaced': is_replace, 'duration_s': result['duration_s'], 'usage': result['usage']})}\n\n"

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
# Validate .docx
# ========================================================================

@app.route("/api/validate/<int:year>/<int:lesson_num>", methods=["POST"])
def api_validate(year, lesson_num):
    from validator import validate_docx
    from generator import OUTPUT_DIR

    data = get_data()
    lesson = _find_lesson(data, year, lesson_num)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    output_folder = lesson.get("output_folder", "").strip("/")
    fname = lesson.get("filename", "")
    if not fname:
        return jsonify({"error": "No filename for this lesson"}), 400

    docx_path = OUTPUT_DIR / output_folder / fname
    if not docx_path.exists():
        # Try various naming patterns
        for pattern in [
            f"L{lesson['lesson_number']:03d} - {lesson['title']}.docx",
            f"L{lesson['lesson_number']:03d} - {lesson.get('required_practical', '')} - {lesson['title']}.docx",
        ]:
            alt = pattern.replace("/", "-").replace(":", " -")
            alt_path = OUTPUT_DIR / output_folder / alt
            if alt_path.exists():
                docx_path = alt_path
                break
        else:
            return jsonify({"error": f"File not found: {docx_path}"}), 404

    try:
        result = validate_docx(str(docx_path))
        if result["valid"]:
            tracker.set_status(year, lesson_num, "qa_passed")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================================================================
# Google Drive upload
# ========================================================================

@app.route("/api/upload/<int:year>/<int:lesson_num>", methods=["POST"])
def api_upload(year, lesson_num):
    from gdrive import upload_booklet
    from generator import OUTPUT_DIR

    data = get_data()
    lesson = _find_lesson(data, year, lesson_num)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    output_folder = lesson.get("output_folder", "").strip("/")
    fname = f"L{lesson['lesson_number']:03d} - {lesson['title']}.docx"
    fname = fname.replace("/", "-").replace(":", " -")
    docx_path = OUTPUT_DIR / output_folder / fname

    if not docx_path.exists():
        return jsonify({"error": f"File not found: {docx_path}. Generate it first."}), 404

    try:
        result = upload_booklet(str(docx_path), lesson)
        tracker.set_status(year, lesson_num, "uploaded")
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
        "openai_key": bool(os.getenv("OPENAI_API_KEY") and
                           not os.getenv("OPENAI_API_KEY", "").startswith("sk-...")),
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
