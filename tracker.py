"""
Progress tracker for booklet production.

Stores status per lesson in a JSON file. Statuses:
  - pending: not yet started
  - generated: prompt sent to Claude, .docx downloaded
  - qa_passed: quality check passed
  - uploaded: uploaded to Google Drive
"""

import json
from pathlib import Path

TRACKER_FILE = Path(__file__).parent / "progress.json"

VALID_STATUSES = ["pending", "generated", "qa_passed", "uploaded"]


def _load():
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text())
    return {}


def _save(data):
    TRACKER_FILE.write_text(json.dumps(data, indent=2))


def _key(year, lesson_num):
    return f"Y{year}_L{lesson_num:03d}"


def get_status(year, lesson_num):
    data = _load()
    return data.get(_key(year, lesson_num), "pending")


def set_status(year, lesson_num, status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
    data = _load()
    data[_key(year, lesson_num)] = status
    _save(data)
    return status


def get_all_statuses():
    return _load()


def get_summary(booklet_lessons):
    """Get status counts from a list of booklet lessons."""
    data = _load()
    counts = {s: 0 for s in VALID_STATUSES}
    for lesson in booklet_lessons:
        key = _key(lesson["year"], lesson["lesson_number"])
        status = data.get(key, "pending")
        counts[status] += 1
    return counts


def bulk_set_status(lessons_keys, status):
    """Set status for multiple lessons at once.
    lessons_keys: list of (year, lesson_num) tuples
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    data = _load()
    for year, lesson_num in lessons_keys:
        data[_key(year, lesson_num)] = status
    _save(data)
