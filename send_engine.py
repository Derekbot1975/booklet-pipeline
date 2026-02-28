"""
SEND Personalisation Engine.

Generates an individually adapted version of a booklet for a student
with special educational needs, based on their EHCP/IEP/ISP.
"""

import logging
import os
import re
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt for SEND adaptation
# ---------------------------------------------------------------------------

SEND_SYSTEM_PROMPT = """You are an expert in Special Educational Needs and Disabilities (SEND) educational adaptations in UK secondary schools.

You will receive:
1. A curriculum booklet for a specific lesson (in markdown format)
2. A student's EHCP/IEP/ISP document describing their individual needs

Your task is to create a PERSONALISED version of the booklet specifically for this student.

ADAPTATION PRINCIPLES:
- Read the student's EHCP/IEP/ISP carefully. Every adaptation must be grounded in their stated needs.
- Preserve the SAME curriculum content and learning objectives — the student must cover the same material as their peers.
- Adapt HOW the content is presented, not WHAT is taught.

COMMON ADAPTATIONS (use only those relevant to this student's needs):
- Simplified vocabulary and sentence structures (for literacy difficulties)
- Chunking content into smaller steps (for processing/attention difficulties)
- Additional scaffolding: sentence starters, word banks, partially completed examples
- Clearer visual layout: more white space, shorter paragraphs, numbered steps
- Modified questions: shorter, clearer phrasing; reduce cognitive load where appropriate
- Extra worked examples where beneficial
- Explicit memory aids (e.g. acronyms, visual reminders of key facts)
- Adjusted reading level while maintaining subject accuracy

FORMATTING RULES — identical to the original booklet:
- NEVER use double asterisks (**) anywhere
- Use UK English spellings throughout
- Maintain heading hierarchy: # H1, ## H2, ### H3
- Bullets use - prefix in knowledge/worked example sections
- Keep ### Worked Example and ### Misconception Box headings exactly

STRUCTURE:
- Keep the same overall section structure as the original booklet
- Add a brief PERSONALISATION NOTE at the very top (after the title block) explaining the key adaptations made, for the student's teacher/support assistant
- The note should be in a simple box format using markdown: > (blockquote)

Return the COMPLETE personalised booklet in markdown. Do not add meta-commentary outside the booklet itself."""


def generate_send_booklet(original_md_path, student, lesson,
                          course_config=None,
                          model="claude-sonnet-4-5-20250929"):
    """
    Generate a SEND-adapted booklet for a specific student.

    Args:
        original_md_path: path to the existing .md booklet
        student: student profile dict (from students.py)
        lesson: lesson dict
        course_config: optional course config dict
        model: Claude model to use

    Returns:
        dict with: md_path, docx_path, pdf_path, usage, duration_s, student
    """
    original_md_path = Path(original_md_path)
    if not original_md_path.exists():
        raise FileNotFoundError(
            f"Original booklet not found: {original_md_path}. "
            "Generate the standard booklet first."
        )

    original_content = original_md_path.read_text(encoding="utf-8")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    # Build student context
    student_name = student.get("name", "Student")
    year = student.get("year", lesson.get("year", ""))
    send_types = student.get("send_types", [])
    document = student.get("document", "").strip()
    notes = student.get("notes", "").strip()

    if not document:
        raise ValueError(
            f"Student profile for '{student_name}' has no EHCP/IEP/ISP document. "
            "Please add their needs document before generating a personalised booklet."
        )

    student_context_parts = [
        f"STUDENT NAME: {student_name}",
    ]
    if year:
        student_context_parts.append(f"YEAR GROUP: Year {year}")
    if send_types:
        student_context_parts.append(f"SEND NEEDS: {', '.join(send_types)}")
    if notes:
        student_context_parts.append(f"TEACHER NOTES: {notes}")

    student_context = "\n".join(student_context_parts)

    user_message = (
        f"STUDENT INFORMATION:\n{student_context}\n\n"
        f"EHCP / IEP / ISP DOCUMENT:\n{document}\n\n"
        f"---\n\n"
        f"ORIGINAL BOOKLET TO ADAPT:\n\n{original_content}"
    )

    from ai_client import create_message

    start = time.time()
    message = create_message(
        model=model,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": SEND_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    duration = time.time() - start

    adapted_content = ""
    for block in message.content:
        if block.type == "text":
            adapted_content += block.text

    if not adapted_content.strip():
        raise RuntimeError("Claude returned empty response for SEND adaptation")

    # Post-process
    from generator import sanitize_markdown, markdown_to_docx, convert_to_pdf

    # The sanitize_markdown function strips blockquotes (>) — we want to keep the
    # personalisation note, so we process it gently: just strip ** and fix spellings
    clean_content = sanitize_markdown(adapted_content)

    # Build output filename: same dir as original, with student name suffix
    safe_student = re.sub(r"[^\w\s-]", "", student_name).strip().replace(" ", "_")
    send_stem = original_md_path.stem + f" - SEND - {safe_student}"
    send_md_path = original_md_path.parent / f"{send_stem}.md"
    send_md_path.write_text(clean_content, encoding="utf-8")

    # Build docx + pdf
    docx_path = markdown_to_docx(str(send_md_path), lesson=lesson)
    pdf_path = convert_to_pdf(docx_path)

    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    if hasattr(message.usage, "cache_creation_input_tokens"):
        usage["cache_creation_input_tokens"] = message.usage.cache_creation_input_tokens
    if hasattr(message.usage, "cache_read_input_tokens"):
        usage["cache_read_input_tokens"] = message.usage.cache_read_input_tokens

    logger.info(
        f"SEND booklet generated for '{student_name}' — "
        f"Y{lesson['year']}_L{lesson['lesson_number']:03d} "
        f"'{lesson.get('title','')}' — {round(duration,1)}s"
    )

    return {
        "md_path": str(send_md_path),
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "usage": usage,
        "model": message.model,
        "duration_s": round(duration, 1),
        "student": {"id": student.get("id"), "name": student_name},
    }
