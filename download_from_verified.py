#!/usr/bin/env python3
"""
Download all VERIFIED specs from spec-urls.json produced by the research agent.
Then import them into the Reference Library.

Usage:
    python download_from_verified.py              # Download all verified PDFs
    python download_from_verified.py --import     # Import into Reference Library
"""

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

SPECS_JSON = Path(__file__).parent / "spec-urls.json"
OUTPUT_DIR = Path(__file__).parent / "data" / "specs-and-nc" / "specifications"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Map from spec-urls.json subject keys to our Reference Library subject names
SUBJECT_MAP = {
    "history": "History",
    "geography": "Geography",
    "english_language": "English",
    "english_literature": "English",
    "english": "English",
    "mathematics": "Mathematics",
    "biology": "Science",
    "chemistry": "Science",
    "physics": "Science",
    "combined_science": "Science",
    "science": "Science",
    "french": "Modern Foreign Languages",
    "spanish": "Modern Foreign Languages",
    "german": "Modern Foreign Languages",
    "italian": "Modern Foreign Languages",
    "religious_studies": "Religious Studies",
    "computer_science": "Computing",
    "computing": "Computing",
    "art_and_design": "Art and Design",
    "music": "Music",
    "physical_education": "Physical Education",
    "drama": "Drama",
    "design_and_technology": "Design and Technology",
    "business": "Business Studies",
    "economics": "Economics",
    "psychology": "Psychology",
    "sociology": "Sociology",
    "statistics": "Statistics",
    "textiles": "Textiles",
    "photography": "Photography",
    "3d_design": "3D Design",
}


def _download(url, dest, retries=3):
    """Download a file with retries."""
    if dest.exists() and dest.stat().st_size > 1000:
        return True

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/pdf,*/*",
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                if len(data) < 1000:
                    return False
                dest.write_bytes(data)
                print(f"  ✅ {dest.name} ({len(data)//1024} KB)")
                return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  ❌ {dest.name}: {e}")
                return False


def download_all():
    """Download all VERIFIED specs from spec-urls.json."""
    data = json.loads(SPECS_JSON.read_text())
    boards_data = data.get("exam_boards", {})
    downloaded = 0
    failed = 0

    for board_key, board_info in boards_data.items():
        board_name = board_info.get("board_name", board_key)
        subjects = board_info.get("subjects", {})
        board_dir = OUTPUT_DIR / board_key
        board_dir.mkdir(exist_ok=True)

        for subj_key, levels in subjects.items():
            for level_key, spec_info in levels.items():
                if not isinstance(spec_info, dict):
                    continue
                status = spec_info.get("status", "")
                url = spec_info.get("spec_pdf", "")

                if status != "VERIFIED" or not url.startswith("http"):
                    continue

                name = spec_info.get("name", subj_key)
                code = spec_info.get("code", "")
                safe_name = f"{board_key}_{level_key}_{subj_key}.pdf".replace("/", "_")
                dest = board_dir / safe_name

                print(f"\n  {board_name} {level_key} {name} ({code})")
                if _download(url, dest):
                    downloaded += 1
                else:
                    failed += 1
                time.sleep(0.3)

    print(f"\n📋 Downloaded: {downloaded}, Failed: {failed}")
    return downloaded, failed


def import_all():
    """Import all downloaded spec PDFs into Reference Library."""
    from reference_library import save_document, list_documents

    data = json.loads(SPECS_JSON.read_text())
    boards_data = data.get("exam_boards", {})
    imported = 0
    errors = 0

    BOARD_NAMES = {
        "aqa": "AQA",
        "edexcel": "Edexcel",
        "ocr": "OCR",
        "wjec": "WJEC",
    }

    for board_key, board_info in boards_data.items():
        board_display = BOARD_NAMES.get(board_key, board_key)
        subjects = board_info.get("subjects", {})
        board_dir = OUTPUT_DIR / board_key

        for subj_key, levels in subjects.items():
            for level_key, spec_info in levels.items():
                if not isinstance(spec_info, dict):
                    continue
                if spec_info.get("status") != "VERIFIED":
                    continue

                safe_name = f"{board_key}_{level_key}_{subj_key}.pdf".replace("/", "_")
                path = board_dir / safe_name
                if not path.exists() or path.stat().st_size < 1000:
                    continue

                # Determine key stage
                level_lower = level_key.lower()
                if "gcse" in level_lower:
                    ks = "KS4"
                elif "a_level" in level_lower or "alevel" in level_lower:
                    ks = "KS5"
                else:
                    ks = "KS4"

                # Map to our subject name
                subject_name = SUBJECT_MAP.get(subj_key, subj_key.replace("_", " ").title())
                spec_name = spec_info.get("name", subj_key)
                title = f"{board_display} {level_key.replace('_', ' ').title()} {spec_name}"

                try:
                    save_document(
                        file_path=str(path),
                        category="ks4_spec",
                        title=title,
                        subject=subject_name,
                        key_stage=ks,
                        exam_board=board_display,
                        description=f"{board_display} {level_key} specification for {spec_name}",
                    )
                    imported += 1
                    print(f"  ✅ {title}")
                except Exception as e:
                    errors += 1

    total = len(list_documents())
    print(f"\n✅ Imported {imported} specs ({errors} errors/duplicates)")
    print(f"📚 Reference Library total: {total} documents")


if __name__ == "__main__":
    import sys
    if "--import" in sys.argv:
        import_all()
    else:
        download_all()
