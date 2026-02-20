"""
Flask app for the booklet production pipeline.

Browse parsed lessons, filter by subject/year/topic, view lesson details,
and generate master prompts ready to paste into Claude Projects.
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from parser import parse_scheme_of_work
from prompt_generator import generate_master_prompt
import tracker

app = Flask(__name__)

XLSX_PATH = "/Users/derek/Downloads/AQA_Combined_Science_Trilogy_Scheme_of_Work.xlsx"

# Parse once at startup
_data = None


def get_data():
    global _data
    if _data is None:
        _data = parse_scheme_of_work(XLSX_PATH)
    return _data


@app.route("/")
def index():
    data = get_data()
    stats = data["stats"]

    # Get unique subjects and topics for filters
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


@app.route("/api/lessons")
def api_lessons():
    data = get_data()
    lessons = data["booklet_lessons"]

    # Apply filters
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

    # Filter by production status
    status_filter = request.args.get("status")
    if status_filter:
        statuses = tracker.get_all_statuses()
        lessons = [
            l for l in lessons
            if statuses.get(f"Y{l['year']}_L{l['lesson_number']:03d}", "pending") == status_filter
        ]

    # Attach status to each lesson
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


# --- Progress tracking ---

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


# --- Batch export ---

EXPORT_DIR = Path(__file__).parent / "prompts"


@app.route("/api/export", methods=["POST"])
def api_export_prompts():
    """Export prompts for filtered lessons to individual .txt files."""
    data = get_data()
    lessons = data["booklet_lessons"]

    body = request.get_json() or {}
    subject = body.get("subject")
    year = body.get("year")
    status_filter = body.get("status")  # only export lessons with this status

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
        # Create subject subdirectory
        subdir = EXPORT_DIR / (l["subject"] or "Unknown")
        subdir.mkdir(exist_ok=True)
        fname = f"L{l['lesson_number']:03d} - {l['title']}.txt"
        # Sanitize filename
        fname = fname.replace("/", "-").replace(":", " -")
        fpath = subdir / fname
        fpath.write_text(prompt)
        exported.append(str(fpath.relative_to(EXPORT_DIR)))

    return jsonify({
        "exported": len(exported),
        "directory": str(EXPORT_DIR),
        "files": exported,
    })


# --- Generate via Claude API ---

@app.route("/api/generate/<int:year>/<int:lesson_num>", methods=["POST"])
def api_generate(year, lesson_num):
    """Generate a booklet via Claude API for a single lesson."""
    from generator import generate_and_save
    from prompt_generator import generate_master_prompt

    data = get_data()
    lesson = None
    for l in data["booklet_lessons"]:
        if l["year"] == year and l["lesson_number"] == lesson_num:
            lesson = l
            break

    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    body = request.get_json() or {}
    model = body.get("model", "claude-sonnet-4-5-20250929")

    prompt = generate_master_prompt(lesson)

    try:
        result = generate_and_save(lesson, prompt, model=model)
        # Auto-update status
        tracker.set_status(year, lesson_num, "generated")
        return jsonify({
            "success": True,
            "md_path": result["md_path"],
            "docx_path": result["docx_path"],
            "usage": result["usage"],
            "model": result["model"],
            "duration_s": result["duration_s"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Validate .docx ---

@app.route("/api/validate/<int:year>/<int:lesson_num>", methods=["POST"])
def api_validate(year, lesson_num):
    """Validate a generated booklet .docx file."""
    from validator import validate_docx
    from generator import OUTPUT_DIR

    data = get_data()
    lesson = None
    for l in data["booklet_lessons"]:
        if l["year"] == year and l["lesson_number"] == lesson_num:
            lesson = l
            break

    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    # Find the docx file
    output_folder = lesson.get("output_folder", "").strip("/")
    fname = lesson.get("filename", "")
    if not fname:
        return jsonify({"error": "No filename for this lesson"}), 400

    docx_path = OUTPUT_DIR / output_folder / fname
    if not docx_path.exists():
        # Try markdown-generated docx (filename might differ)
        alt_fname = f"L{lesson['lesson_number']:03d} - {lesson['title']}.docx"
        alt_fname = alt_fname.replace("/", "-").replace(":", " -")
        docx_path = OUTPUT_DIR / output_folder / alt_fname
        if not docx_path.exists():
            return jsonify({"error": f"File not found: {docx_path}"}), 404

    try:
        result = validate_docx(str(docx_path))
        if result["valid"]:
            tracker.set_status(year, lesson_num, "qa_passed")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Google Drive upload ---

@app.route("/api/upload/<int:year>/<int:lesson_num>", methods=["POST"])
def api_upload(year, lesson_num):
    """Upload a generated booklet to Google Drive."""
    from gdrive import upload_booklet
    from generator import OUTPUT_DIR

    data = get_data()
    lesson = None
    for l in data["booklet_lessons"]:
        if l["year"] == year and l["lesson_number"] == lesson_num:
            lesson = l
            break

    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    # Find the docx file
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
    """Check Google Drive connection status."""
    from gdrive import check_connection
    return jsonify(check_connection())


# --- Config/setup status ---

@app.route("/api/config")
def api_config():
    """Check which integrations are configured."""
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
    """Read the .env file (masking sensitive values)."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return jsonify({"exists": False, "content": ""})
    raw = env_path.read_text()
    return jsonify({"exists": True, "content": raw})


@app.route("/api/env", methods=["POST"])
def api_env_write():
    """Write the .env file and reload env vars."""
    body = request.get_json() or {}
    content = body.get("content", "")
    env_path = Path(__file__).parent / ".env"
    env_path.write_text(content)
    # Reload env vars into this process
    from dotenv import load_dotenv
    load_dotenv(override=True)
    return jsonify({"saved": True})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
