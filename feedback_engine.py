"""
Feedback Engine — applies teacher feedback to an existing booklet.

Teacher writes freeform notes (e.g. "section 2 is too complex,
simplify the language") and Claude makes targeted edits.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

FEEDBACK_DIR = Path(__file__).parent / "data" / "feedback"
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# System prompt for the feedback editor
# ---------------------------------------------------------------------------

FEEDBACK_SYSTEM_PROMPT = """You are an expert educational content editor working on structured curriculum booklets.

You will receive:
1. A complete booklet in markdown format
2. Teacher feedback describing what to change

Your task is to make targeted edits to the booklet based on the feedback.

RULES — follow every one:
- Make ONLY the changes the teacher has requested. Do not alter anything else.
- Preserve all formatting conventions exactly:
  * NEVER use double asterisks (**) anywhere
  * Use UK English spellings throughout
  * Maintain all section headings at their correct levels (# H1, ## H2, ### H3)
  * Keep bullet points as - prefix, never numbered in knowledge/worked example sections
  * Preserve all ### Worked Example and ### Misconception Box headings exactly
- Return the COMPLETE edited booklet in markdown — not just the changed sections.
- Do not add commentary or explanations. Output only the booklet markdown.
- If the feedback is unclear or contradictory, use your best judgement to make a sensible edit."""


def _feedback_record_path(course_id, year, lesson_num):
    """Return the JSON path for feedback history for a lesson."""
    return FEEDBACK_DIR / course_id / f"Y{year}_L{lesson_num:03d}.json"


def load_feedback_history(course_id, year, lesson_num):
    """Load all feedback records for a lesson. Returns a list."""
    path = _feedback_record_path(course_id, year, lesson_num)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def _save_feedback_record(course_id, year, lesson_num, record):
    """Append a feedback record to the history file."""
    path = _feedback_record_path(course_id, year, lesson_num)
    path.parent.mkdir(parents=True, exist_ok=True)
    history = load_feedback_history(course_id, year, lesson_num)
    history.append(record)
    path.write_text(json.dumps(history, indent=2))


def apply_feedback(md_path, feedback_text, lesson, course_id,
                   model="claude-sonnet-4-5-20250929"):
    """
    Apply teacher feedback to an existing booklet.

    Args:
        md_path: absolute path to the existing .md file
        feedback_text: teacher's freeform feedback string
        lesson: lesson dict (for metadata)
        course_id: active course ID
        model: Claude model to use

    Returns:
        dict with keys: md_path, docx_path, pdf_path, usage, duration_s,
                        feedback_text, changes_summary
    """
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Booklet not found: {md_path}")

    original_content = md_path.read_text(encoding="utf-8")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    from ai_client import create_message

    # Back up original before editing
    version_num = len(load_feedback_history(course_id, lesson["year"],
                                             lesson["lesson_number"])) + 1
    backup_path = md_path.with_stem(md_path.stem + f"_v{version_num}_pre")
    backup_path.write_text(original_content, encoding="utf-8")

    user_message = (
        f"TEACHER FEEDBACK:\n{feedback_text}\n\n"
        f"---\n\n"
        f"CURRENT BOOKLET:\n\n{original_content}"
    )

    start = time.time()
    message = create_message(
        model=model,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": FEEDBACK_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    duration = time.time() - start

    edited_content = ""
    for block in message.content:
        if block.type == "text":
            edited_content += block.text

    if not edited_content.strip():
        raise RuntimeError("Claude returned empty response for feedback edit")

    # Sanitise (apply same post-processing as generation)
    from generator import sanitize_markdown, markdown_to_docx, convert_to_pdf
    clean_content = sanitize_markdown(edited_content)

    # Save edited markdown (overwriting the booklet)
    md_path.write_text(clean_content, encoding="utf-8")

    # Rebuild docx + pdf
    docx_path = markdown_to_docx(str(md_path), lesson=lesson)
    pdf_path = convert_to_pdf(docx_path)

    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    if hasattr(message.usage, "cache_creation_input_tokens"):
        usage["cache_creation_input_tokens"] = message.usage.cache_creation_input_tokens
    if hasattr(message.usage, "cache_read_input_tokens"):
        usage["cache_read_input_tokens"] = message.usage.cache_read_input_tokens

    # Save record
    record = {
        "applied_at": datetime.now().isoformat(),
        "feedback_text": feedback_text,
        "version_before": str(backup_path.name),
        "model": message.model,
        "usage": usage,
        "duration_s": round(duration, 1),
    }
    _save_feedback_record(course_id, lesson["year"], lesson["lesson_number"], record)

    logger.info(
        f"Feedback applied to Y{lesson['year']}_L{lesson['lesson_number']:03d} "
        f"'{lesson.get('title','')}' — {len(feedback_text)} chars feedback, "
        f"{round(duration,1)}s"
    )

    return {
        "md_path": str(md_path),
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "usage": usage,
        "model": message.model,
        "duration_s": round(duration, 1),
        "feedback_text": feedback_text,
        "backup_path": str(backup_path),
    }
