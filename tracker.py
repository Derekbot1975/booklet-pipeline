"""
Progress tracker for booklet production.

Stores status per lesson in a JSON file, scoped by course ID. Statuses:
  - pending: not yet started
  - generated: prompt sent to Claude, .docx downloaded
  - qa_passed: quality check passed
  - uploaded: uploaded to Google Drive
"""

import json
from pathlib import Path

TRACKER_FILE = Path(__file__).parent / "progress.json"

VALID_STATUSES = ["pending", "generated", "qa_passed", "uploaded"]

_SEPARATOR = "__"
_DEFAULT_COURSE = "aqa-combined-science"


def _load():
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text())
    return {}


def _save(data):
    TRACKER_FILE.write_text(json.dumps(data, indent=2))


def _key(year, lesson_num, course_id=None):
    cid = course_id or _DEFAULT_COURSE
    return f"{cid}{_SEPARATOR}Y{year}_L{lesson_num:03d}"


def _migrate_if_needed(data):
    """Migrate old keys (without course prefix) to new format."""
    migrated = False
    old_keys = [k for k in data if _SEPARATOR not in k]
    for old_key in old_keys:
        new_key = f"{_DEFAULT_COURSE}{_SEPARATOR}{old_key}"
        if new_key not in data:
            data[new_key] = data[old_key]
        del data[old_key]
        migrated = True
    if migrated:
        _save(data)
    return data


def get_status(year, lesson_num, course_id=None):
    data = _migrate_if_needed(_load())
    return data.get(_key(year, lesson_num, course_id), "pending")


def set_status(year, lesson_num, status, course_id=None):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
    data = _migrate_if_needed(_load())
    data[_key(year, lesson_num, course_id)] = status
    _save(data)
    return status


def get_all_statuses(course_id=None):
    """Get all statuses, filtered to a specific course if provided."""
    data = _migrate_if_needed(_load())
    if course_id is None:
        return data
    prefix = f"{course_id}{_SEPARATOR}"
    return {k: v for k, v in data.items() if k.startswith(prefix)}


def get_summary(booklet_lessons, course_id=None):
    """Get status counts from a list of booklet lessons."""
    data = _migrate_if_needed(_load())
    counts = {s: 0 for s in VALID_STATUSES}
    for lesson in booklet_lessons:
        key = _key(lesson["year"], lesson["lesson_number"], course_id)
        status = data.get(key, "pending")
        counts[status] += 1
    return counts


def bulk_set_status(lessons_keys, status, course_id=None):
    """Set status for multiple lessons at once.
    lessons_keys: list of (year, lesson_num) tuples
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    data = _migrate_if_needed(_load())
    for year, lesson_num in lessons_keys:
        data[_key(year, lesson_num, course_id)] = status
    _save(data)
