"""
Course configuration management.

Stores uploaded scheme-of-work courses as JSON configs. Each course describes
a subject area (e.g. "AQA Combined Science", "KS3 Geography") with its
spreadsheet path, column mapping, sheet names, key stage, exam board, and
topic folder mappings.

The existing AQA Combined Science pipeline is auto-registered as the default
course so that everything works out of the box without any uploads.
"""

import json
import uuid
from pathlib import Path

COURSES_DIR = Path(__file__).parent / "courses"
COURSES_DIR.mkdir(exist_ok=True)

# --- Default AQA Combined Science course (migrated from parser.py) ---

_DEFAULT_AQA_ID = "aqa-combined-science"

_DEFAULT_AQA_CONFIG = {
    "id": _DEFAULT_AQA_ID,
    "name": "AQA Combined Science: Trilogy",
    "exam_board": "AQA",
    "qualification": "GCSE",
    "key_stage": 4,
    "subjects": ["Biology", "Chemistry", "Physics"],
    "xlsx_path": "/Users/derek/Downloads/AQA_Combined_Science_Trilogy_Scheme_of_Work.xlsx",
    "sheets": [
        {"name": "Year 10 Lessons", "year": 10},
        {"name": "Year 11 Lessons", "year": 11},
    ],
    "header_row": 4,
    "col_map": {
        "week": 0,
        "lesson_num": 1,
        "subject": 2,
        "topic": 3,
        "title": 4,
        "spec_content": 5,
        "rp": 6,
        "key_vocabulary": 7,
        "ws_ms": 8,
        "ht_only": 9,
    },
    "topic_folders": {
        "B1": "B1 - Cell Biology",
        "B2": "B2 - Organisation",
        "B3": "B3 - Infection and Response",
        "B4": "B4 - Bioenergetics",
        "B5": "B5 - Homeostasis and Response",
        "B6": "B6 - Inheritance Variation and Evolution",
        "B7": "B7 - Ecology",
        "C8": "C8 - Atomic Structure and Periodic Table",
        "C9": "C9 - Bonding Structure and Properties",
        "C10": "C10 - Quantitative Chemistry",
        "C11": "C11 - Chemical Changes",
        "C12": "C12 - Energy Changes",
        "C13": "C13 - Rate and Extent of Chemical Change",
        "C14": "C14 - Organic Chemistry",
        "C15": "C15 - Chemical Analysis",
        "C16": "C16 - Chemistry of the Atmosphere",
        "C17": "C17 - Using Resources",
        "P18": "P18 - Energy",
        "P19": "P19 - Electricity",
        "P20": "P20 - Particle Model of Matter",
        "P21": "P21 - Atomic Structure",
        "P22": "P22 - Forces",
        "P23": "P23 - Waves",
        "P24": "P24 - Magnetism and Electromagnetism",
    },
    "subject_from_topic_prefix": {
        "B": "Biology",
        "C": "Chemistry",
        "P": "Physics",
    },
    "topic_code_pattern": r"([BCP]\d+)",
    "system_prompt_context": (
        "AQA GCSE Combined Science: Trilogy (8464)"
    ),
    "prior_knowledge_base": "Students have completed standard KS3 science.",
    "gdrive_folder_id": "",  # Optional: per-course Google Drive folder ID
    "is_default": True,
}


def _config_path(course_id):
    return COURSES_DIR / f"{course_id}.json"


def _ensure_default():
    """Write the default AQA config if it doesn't exist yet."""
    path = _config_path(_DEFAULT_AQA_ID)
    if not path.exists():
        path.write_text(json.dumps(_DEFAULT_AQA_CONFIG, indent=2))


# Ensure default exists on import
_ensure_default()


def list_courses():
    """Return list of all course configs (summary only)."""
    courses = []
    for p in sorted(COURSES_DIR.glob("*.json")):
        try:
            cfg = json.loads(p.read_text())
            courses.append({
                "id": cfg["id"],
                "name": cfg["name"],
                "exam_board": cfg.get("exam_board", ""),
                "key_stage": cfg.get("key_stage", ""),
                "qualification": cfg.get("qualification", ""),
                "subjects": cfg.get("subjects", []),
                "is_default": cfg.get("is_default", False),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return courses


def get_course(course_id):
    """Load full course config by ID."""
    path = _config_path(course_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_course(config):
    """Save a course config. Generates ID if not present."""
    if "id" not in config or not config["id"]:
        config["id"] = str(uuid.uuid4())[:8]
    path = _config_path(config["id"])
    path.write_text(json.dumps(config, indent=2))
    return config


def delete_course(course_id):
    """Delete a course config. Cannot delete the default."""
    if course_id == _DEFAULT_AQA_ID:
        raise ValueError("Cannot delete the default course.")
    path = _config_path(course_id)
    if path.exists():
        path.unlink()
        return True
    return False


def get_default_course_id():
    """Return the ID of the default course."""
    return _DEFAULT_AQA_ID
