"""
SEND student profile management.

Stores and retrieves EHCP/IEP/ISP profiles for individual students.
Profiles are saved as JSON files in data/students/.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

STUDENTS_DIR = Path(__file__).parent / "data" / "students"
STUDENTS_DIR.mkdir(parents=True, exist_ok=True)


def _student_path(student_id):
    return STUDENTS_DIR / f"{student_id}.json"


def list_students():
    """Return all student profiles as a list, sorted by name."""
    profiles = []
    for p in sorted(STUDENTS_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            profiles.append(data)
        except Exception:
            continue
    return sorted(profiles, key=lambda s: s.get("name", "").lower())


def get_student(student_id):
    """Get a single student profile. Returns None if not found."""
    path = _student_path(student_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def save_student(profile):
    """
    Create or update a student profile.

    Expected profile fields:
        name (str, required)
        year (int, optional)
        send_types (list of str, optional) e.g. ["Dyslexia", "ASD", "EHC Plan"]
        document (str) — full EHCP/IEP/ISP text
        notes (str) — optional extra teacher notes

    Returns the saved profile dict (with id and timestamps).
    """
    if not profile.get("name", "").strip():
        raise ValueError("Student name is required")

    if "id" not in profile or not profile["id"]:
        profile["id"] = str(uuid.uuid4())[:8]
        profile["created_at"] = datetime.now().isoformat()

    profile["updated_at"] = datetime.now().isoformat()

    path = _student_path(profile["id"])
    path.write_text(json.dumps(profile, indent=2))
    return profile


def delete_student(student_id):
    """Delete a student profile. Raises ValueError if not found."""
    path = _student_path(student_id)
    if not path.exists():
        raise ValueError(f"Student not found: {student_id}")
    path.unlink()
