"""
Booklet Types Engine (Prompt Sheet 15).

Generates three additional booklet types from existing lesson content:
  - TEACHING BOOKLET (Student + Teacher paired versions)
  - REFLECTION / ABSENCE BOOKLET (fully self-contained for independent work)
  - REVISION BOOKLET (evidence-based revision techniques per unit)

Each type has its own specialised system prompt and output structure.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

VALID_TYPES = {
    "teaching_student",
    "teaching_teacher",
    "reflection",
    "revision",
}

# ───────────────────────────────────────────────────────────────────
# System prompts per booklet type
# ───────────────────────────────────────────────────────────────────

TEACHING_STUDENT_PROMPT = """You are a specialist educational content creator producing a STUDENT booklet
for use IN THE CLASSROOM with teacher guidance.

LANGUAGE: Use UK English throughout (organise, colour, centre, analyse, etc.).

CRITICAL FORMATTING RULES:
- NEVER use double asterisks (**). Emphasis via headings or plain text only.
- Return the complete booklet in markdown format.

STUDENT BOOKLET STRUCTURE:
1. TITLE BLOCK:
   Teaching Booklet — Student Version
   Subject: [Subject]
   Lesson: [Number] — [Title]
   Date: _______________

2. LEARNING OBJECTIVES:
   "By the end of this lesson, I can..."
   - (student-friendly "I can..." statements)

3. STARTER ACTIVITY (5 minutes):
   A short retrieval or engagement task.

4. KEY VOCABULARY:
   Table of key terms with definitions.

5. GUIDED NOTES (main content):
   - Knowledge sections with GAPS for students to fill in
   - Diagrams to label or complete (describe what students should draw)
   - Note-taking spaces: indicate with [WRITE YOUR ANSWER HERE] or blank lines (_____)

6. WORKED EXAMPLE:
   Step-by-step worked example relevant to the lesson content.

7. PRACTICE QUESTIONS (scaffolded):
   - Bronze / Silver / Gold difficulty levels
   - Space for answers indicated with blank lines

8. REFLECTION:
   - "Rate your confidence 1-5 for today's lesson"
   - "What is one thing you learned today?"
   - "What question would you ask your teacher?"

RULES:
- Do NOT include model answers (teacher version only).
- Do NOT include teacher instructions or timing.
- Leave CLEAR space for student writing (use _____ lines).
- Make it visually clean and spacious.
- Content should follow logically from the lesson data provided."""

TEACHING_TEACHER_PROMPT = """You are a specialist educational content creator producing a TEACHER booklet
that mirrors the student version but includes full teaching guidance.

LANGUAGE: Use UK English throughout.

CRITICAL FORMATTING RULES:
- NEVER use double asterisks (**). Emphasis via headings or plain text only.
- Return the complete booklet in markdown format.
- Teacher-only content must be clearly marked with [TEACHER NOTE: ...]

TEACHER BOOKLET STRUCTURE:
Include EVERYTHING from the student version, PLUS:

1. TITLE BLOCK (same as student + "Teacher Edition")

2. LESSON OVERVIEW [TEACHER NOTE]:
   - Total lesson time and section breakdown
   - Resources needed
   - Prior knowledge assumed

3. For EACH section, add [TEACHER NOTE] blocks with:
   - TIMING: "This section: X minutes"
   - DELIVERY: "Read aloud, then ask students to..."
   - QUESTIONING SCRIPT: Exact questions with expected answers
   - DIFFERENTIATION: "For higher: ... / For lower: ... / For SEND: ..."
   - COMMON MISCONCEPTIONS: What to watch for at this point

4. MODEL ANSWERS for ALL questions — marked as:
   [TEACHER NOTE — MODEL ANSWER]: ...

5. ASSESSMENT CHECKPOINTS:
   [TEACHER NOTE — CHECK]: "Pause here. Circulate and check..."

6. PLENARY SUGGESTIONS:
   [TEACHER NOTE — PLENARY]: Options for closing the lesson.

7. EXTENSION ACTIVITIES:
   [TEACHER NOTE — EXTENSION]: For students who finish early.

RULES:
- The student-visible content must be IDENTICAL to the student version.
- Teacher content is ADDITIONAL, clearly marked with [TEACHER NOTE].
- Include a full teaching script — explicit enough for a non-specialist cover teacher.
- Include timing for every section (must total the lesson length).
- Include exact questions to ask with expected answers."""

REFLECTION_PROMPT = """You are a specialist educational content creator producing a COMPLETELY
SELF-CONTAINED booklet for independent study.

CRITICAL REQUIREMENT: A student must be able to complete this booklet with
ZERO teacher support and ZERO additional resources. Everything they need
must be in the booklet itself.

LANGUAGE: Use UK English throughout.

CRITICAL FORMATTING RULES:
- NEVER use double asterisks (**).
- Return the complete booklet in markdown format.

SELF-CONTAINED BOOKLET STRUCTURE:

1. TITLE:
   Independent Study: [Topic]
   Subject: [Subject]
   Lesson: [Number] — [Title]
   Estimated time: [X] minutes

2. HOW TO USE THIS BOOKLET:
   Brief instructions explaining that this is a self-study resource.
   "Work through each section in order. Check your answers at the back."

3. LEARNING OBJECTIVES:
   Clear "By the end, you will be able to..." statements.

4. KEY VOCABULARY:
   Complete definitions table — students need these to understand the content.

5. KNOWLEDGE SECTIONS (the TEACHING content):
   - Present ALL information the student needs — do NOT assume prior knowledge.
   - Break into digestible chunks (1-2 paragraphs each).
   - After EACH chunk: 2-3 comprehension questions.
   - Include diagrams described in text (what to draw/label).

6. WORKED EXAMPLES:
   For any mathematical/procedural content, full step-by-step examples.

7. PRACTICE EXERCISES:
   Scaffolded questions with space to work (_____ lines).

8. SELF-CHECK ANSWERS:
   ## Answers (Check After Completing)
   All answers to comprehension and practice questions.
   Clear mark allocation for each question.

9. SELF-ASSESSMENT REFLECTION:
   - "How confident are you with this topic? (1-5)"
   - "What did you find most challenging?"
   - "What question would you ask your teacher?"

RULES:
- This booklet must TEACH, not just test.
- Include ALL information needed — assume no textbook, no internet, no teacher.
- Self-check answers MUST be included.
- Suitable for: home learning, detention, absence catch-up, cover lessons."""

REVISION_PROMPT = """You are a specialist educational content creator producing a REVISION BOOKLET
using the world's best evidence-based revision techniques.

LANGUAGE: Use UK English throughout.

CRITICAL FORMATTING RULES:
- NEVER use double asterisks (**).
- Return the complete booklet in markdown format.

REVISION SCIENCE PRINCIPLES TO APPLY:
- Retrieval practice is more effective than re-reading
- Spaced practice beats massed practice
- Interleaving improves long-term retention
- Self-testing with feedback is essential
- Dual coding (words + visuals) aids memory

REVISION BOOKLET STRUCTURE:

1. TITLE:
   Revision Booklet: [Unit Title]
   Subject: [Subject]
   Covering lessons: [range]

2. KNOWLEDGE ORGANISER (1 page max):
   Concise summary of ALL key facts, definitions, and concepts.
   Organised by sub-topic in a clear table or structured format.

3. TEST YOURSELF — Retrieval Practice:
   Questions covering the full unit. Mix of:
   - Quick-fire recall (1-word or short answers)
   - "Explain why..." questions
   - "Describe how..." questions
   NO notes allowed — test from memory!

4. CHECK YOUR ANSWERS:
   Model answers for all retrieval questions.
   Students mark their own work.

5. APPLY IT — Exam-Style Questions:
   3-5 longer questions in exam format with mark allocations.
   Include command words: Explain, Compare, Evaluate, Describe.

6. MARK SCHEMES:
   Full mark schemes for exam-style questions.
   Indicative content + mark points.

7. LINK IT — Cross-Topic Connections:
   How this unit connects to other topics studied.
   "What you learned in [Unit X] helps you understand [this concept] because..."

8. REVISE IT DIFFERENTLY — Dual Coding Activities:
   a) Sketch a key diagram from memory, then check against the knowledge organiser.
   b) Create a mind map connecting the key concepts.
   c) Write a summary of the whole unit in exactly 50 words.
   d) Teach it: write a script explaining the topic to someone who knows nothing about it.

9. RATE YOURSELF — Self-Assessment:
   RAG (Red/Amber/Green) rating for each sub-topic.
   Table with: Sub-topic | Confidence (R/A/G) | Action needed

10. WHAT NEXT? — Action Plan:
    Based on self-assessment, identify focus areas.

RULES:
- Revision should be ACTIVE, not passive re-reading.
- Mix question types and difficulty levels.
- Include earlier topics for spaced practice (interleaving).
- Cover the ENTIRE unit content — not just highlights."""


def _get_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _get_system_prompt(booklet_type):
    """Get the system prompt for a specific booklet type."""
    prompts = {
        "teaching_student": TEACHING_STUDENT_PROMPT,
        "teaching_teacher": TEACHING_TEACHER_PROMPT,
        "reflection": REFLECTION_PROMPT,
        "revision": REVISION_PROMPT,
    }
    return prompts.get(booklet_type, "")


# ───────────────────────────────────────────────────────────────────
# Generation
# ───────────────────────────────────────────────────────────────────

def generate_typed_booklet(lesson, booklet_type, course_config,
                           existing_booklet_content=None,
                           reference_context="",
                           unit_lessons=None,
                           model="claude-sonnet-4-5-20250929"):
    """
    Generate a specific type of booklet for a lesson.

    Args:
        lesson: Lesson data dict from the parser
        booklet_type: One of VALID_TYPES
        course_config: Course configuration dict
        existing_booklet_content: Markdown content of the existing pipeline booklet (if any)
        reference_context: Reference document context string
        unit_lessons: For revision booklets, all lessons in the unit
        model: Claude model to use

    Returns:
        Dict with md_path, docx_path, pdf_path, usage, model, duration_s
    """
    if booklet_type not in VALID_TYPES:
        raise ValueError(f"Invalid booklet type: {booklet_type}. Must be one of: {VALID_TYPES}")

    system_prompt = _get_system_prompt(booklet_type)
    if not system_prompt:
        raise ValueError(f"No system prompt for type: {booklet_type}")

    client = _get_client()
    start = time.time()

    # Build user prompt
    user_parts = []
    user_parts.append(f"Generate a {booklet_type.replace('_', ' ').upper()} booklet for this lesson:")
    user_parts.append(f"\nLESSON DATA:")
    user_parts.append(f"  Subject: {lesson.get('subject', 'Unknown')}")
    user_parts.append(f"  Topic: {lesson.get('topic', 'Unknown')}")
    user_parts.append(f"  Year: {lesson.get('year', '?')}")
    user_parts.append(f"  Lesson Number: {lesson.get('lesson_number', '?')}")
    user_parts.append(f"  Title: {lesson.get('title', 'Unknown')}")
    user_parts.append(f"  Specification Content: {lesson.get('spec_content', 'N/A')}")
    user_parts.append(f"  Key Vocabulary: {lesson.get('key_vocabulary', 'N/A')}")
    if lesson.get("rp"):
        user_parts.append(f"  Required Practical: {lesson['rp']}")

    if existing_booklet_content:
        user_parts.append(f"\nEXISTING PIPELINE BOOKLET (use as content source):\n{existing_booklet_content}")

    if reference_context:
        user_parts.append(f"\nREFERENCE MATERIALS:\n{reference_context}")

    if booklet_type == "revision" and unit_lessons:
        user_parts.append(f"\nALL LESSONS IN THIS UNIT (for revision coverage):")
        for ul in unit_lessons:
            user_parts.append(f"  L{ul.get('lesson_number', '?')}: {ul.get('title', '')} — {ul.get('spec_content', '')}")

    user_prompt = "\n".join(user_parts)

    system_parts = [
        {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        system=system_parts,
        messages=[{"role": "user", "content": user_prompt}],
    )

    duration = round(time.time() - start, 1)
    content = response.content[0].text.strip()

    # Sanitise and save
    from generator import sanitize_markdown, markdown_to_docx, convert_to_pdf, OUTPUT_DIR

    content = sanitize_markdown(content)

    # Build output path: same directory as the lesson's normal booklet
    from generator import check_existing_booklet
    existing = check_existing_booklet(lesson)

    if existing["exists"]:
        base_dir = Path(existing["docx_path"]).parent
        base_stem = Path(existing["docx_path"]).stem
    else:
        # Build path from course config
        course_name = course_config.get("name", "Unknown")
        safe_course = re.sub(r"[^\w\s-]", "", course_name).replace(" ", "_")
        subject = lesson.get("subject", "General")
        topic = lesson.get("topic", "General")
        safe_topic = re.sub(r"[^\w\s-]", "", topic).replace(" ", "_")
        base_dir = OUTPUT_DIR / safe_course / subject / safe_topic
        ln = lesson.get("lesson_number", 0)
        title = lesson.get("title", "Untitled")
        safe_title = re.sub(r"[^\w\s-]", "", title).replace(" ", "_")
        base_stem = f"L{ln:03d}_-_{safe_title}"

    base_dir.mkdir(parents=True, exist_ok=True)

    # Type suffix mapping
    type_suffix = {
        "teaching_student": "Teaching_Student",
        "teaching_teacher": "Teaching_Teacher",
        "reflection": "Reflection",
        "revision": "Revision",
    }
    suffix = type_suffix.get(booklet_type, booklet_type)
    filename = f"{base_stem} - {suffix}"

    md_path = base_dir / f"{filename}.md"
    md_path.write_text(content, encoding="utf-8")

    docx_path = markdown_to_docx(str(md_path))
    pdf_path = convert_to_pdf(docx_path)

    return {
        "booklet_type": booklet_type,
        "md_path": str(md_path),
        "docx_path": str(docx_path) if docx_path else None,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        "model": model,
        "duration_s": duration,
    }


def list_typed_booklets(lesson, booklet_type=None):
    """List all typed booklets that exist for a lesson."""
    from generator import check_existing_booklet

    existing = check_existing_booklet(lesson)
    if not existing["exists"]:
        return []

    base_dir = Path(existing["docx_path"]).parent
    base_stem = Path(existing["docx_path"]).stem

    type_suffixes = ["Teaching_Student", "Teaching_Teacher", "Reflection", "Revision"]
    booklets = []

    for suffix in type_suffixes:
        pattern = f"{base_stem} - {suffix}.docx"
        docx = base_dir / pattern
        if docx.exists():
            btype = suffix.lower().replace(" ", "_")
            if booklet_type and btype != booklet_type:
                continue
            booklets.append({
                "type": btype,
                "type_label": suffix.replace("_", " "),
                "docx_path": str(docx),
                "pdf_exists": docx.with_suffix(".pdf").exists(),
                "md_exists": docx.with_suffix(".md").exists(),
            })

    return booklets
