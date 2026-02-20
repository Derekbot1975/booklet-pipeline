"""
Generates the master prompt for a single booklet lesson,
ready to paste into a Claude Project conversation.

Adapts to any subject/course via course_config.
"""


def generate_master_prompt(lesson, course_config=None):
    """
    Build the master prompt from a lesson dict.

    Args:
        lesson: dict from parser with all lesson fields
        course_config: optional course config dict (from courses.py)

    Returns:
        str: the complete prompt text
    """
    subject = lesson["subject"] or "Unknown"
    topic = lesson["topic"] or "Unknown"
    title = lesson["title"] or "Unknown"
    year = lesson["year"]
    lesson_num = lesson["lesson_number"]
    spec_content = lesson["spec_content"] or "None"
    rp = lesson.get("required_practical") or "None"
    key_vocab = lesson.get("key_vocabulary") or "None"
    ws_ms = lesson.get("ws_ms") or "None"
    ht_only = lesson.get("ht_only") or "None"
    prior_lessons = lesson.get("prior_lessons", [])

    # Build prior knowledge string from course config
    prior_base = "Students have completed standard KS3 science."
    if course_config:
        prior_base = course_config.get("prior_knowledge_base", prior_base)

    if not prior_lessons:
        prior_knowledge = prior_base
    else:
        prior_list = "\n".join(f"  - {t}" for t in prior_lessons)
        prior_knowledge = (
            f"{prior_base} "
            "Students have also completed all preceding lessons in the "
            "scheme of work up to this point:\n" + prior_list
        )

    # Core fields present for all courses
    lines = [
        "Create a complete self-study booklet (.docx) for the following lesson:",
        "",
        f"SUBJECT: {subject}",
        "",
        f"TOPIC: {topic}",
        "",
        f"LESSON TITLE: {title}",
        "",
        f"LESSON NUMBER: Lesson {lesson_num} in Year {year}",
        "",
        f"SPECIFICATION CONTENT: {spec_content}",
    ]

    # Optional fields — only include if the column is mapped
    col_map = {}
    if course_config:
        col_map = course_config.get("col_map", {})

    # Required Practical — include if mapped or has a value
    if col_map.get("rp") is not None or rp != "None":
        lines += ["", f"REQUIRED PRACTICAL: {rp}"]

    # Key Vocabulary
    if col_map.get("key_vocabulary") is not None or key_vocab != "None":
        lines += ["", f"KEY VOCABULARY: {key_vocab}"]

    # WS/MS skills
    if col_map.get("ws_ms") is not None or ws_ms != "None":
        lines += ["", f"WORKING SCIENTIFICALLY / MATHS SKILLS: {ws_ms}"]

    # HT only content
    if col_map.get("ht_only") is not None or ht_only != "None":
        lines += ["", f"HT ONLY CONTENT: {ht_only}"]

    lines += [
        "",
        f"PRIOR KNOWLEDGE: {prior_knowledge}",
        "",
        _get_formatting_rules(),
        "",
        "Please create the booklet now, following the Prompt System v1.1 framework exactly. Save as a .docx file.",
    ]

    return "\n".join(lines)


def _get_formatting_rules():
    """Standard formatting rules appended to every prompt."""
    return """FORMATTING RULES (MUST follow — no exceptions):
- Use UK English spellings throughout (e.g. organise, colour, centre, analyse, labelled, modelling, defence, fibre, travelled, minimise, recognise, sulphur, aluminium, haemoglobin)
- NEVER use double asterisks (**) anywhere in your output
- Knowledge Content sections: use bullet points (- prefix), NEVER numbered lists
- Worked Examples: use bullet points (- prefix), NEVER numbered lists
- UNIVERSAL NUMBERING RESTART: Every distinct numbered section MUST start at 1. No section continues numbering from a previous section:
  * Knowledge Check Questions: restart at 1 for EACH Knowledge Chunk
  * Application Questions / Calculations: start at 1
  * Topics to Revisit: numbered 1, 2, 3 (three slots)
  * Targets for Next Lesson: numbered 1, 2, 3 (three slots)
  * The ONLY exception is the Holistic Recall Starter (1-20 continuous)
- Mark scheme numbering must match question numbering exactly — restart per chunk AND per section (Application Questions get their own mark scheme starting at 1)
- Title block must be single-spaced (one line per field, no blank lines between them)
- Key Vocabulary tables: Term | Definition format, no asterisks"""
