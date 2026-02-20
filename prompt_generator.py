"""
Generates the master prompt for a single booklet lesson,
ready to paste into a Claude Project conversation.
"""


def generate_master_prompt(lesson):
    """
    Build the master prompt from a lesson dict.

    Args:
        lesson: dict from parser with all lesson fields

    Returns:
        str: the complete prompt text
    """
    subject = lesson["subject"] or "Unknown"
    topic = lesson["topic"] or "Unknown"
    title = lesson["title"] or "Unknown"
    year = lesson["year"]
    lesson_num = lesson["lesson_number"]
    spec_content = lesson["spec_content"] or "None"
    rp = lesson["required_practical"] or "None"
    key_vocab = lesson["key_vocabulary"] or "None"
    ws_ms = lesson["ws_ms"] or "None"
    ht_only = lesson["ht_only"] or "None"
    prior_lessons = lesson.get("prior_lessons", [])

    # Build prior knowledge string
    if not prior_lessons:
        prior_knowledge = "Students have completed standard KS3 science."
    else:
        prior_list = "\n".join(f"  - {t}" for t in prior_lessons)
        prior_knowledge = (
            "Students have completed standard KS3 science. "
            "Students have also completed all preceding lessons in the "
            "scheme of work up to this point:\n" + prior_list
        )

    prompt = f"""Create a complete self-study booklet (.docx) for the following lesson:

SUBJECT: {subject}

TOPIC: {topic}

LESSON TITLE: {title}

LESSON NUMBER: Lesson {lesson_num} in Year {year}

SPECIFICATION CONTENT: {spec_content}

REQUIRED PRACTICAL: {rp}

KEY VOCABULARY: {key_vocab}

WORKING SCIENTIFICALLY / MATHS SKILLS: {ws_ms}

HT ONLY CONTENT: {ht_only}

PRIOR KNOWLEDGE: {prior_knowledge}

FORMATTING RULES (MUST follow — no exceptions):
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
- Drawing spaces: output [DRAWING SPACE: detailed description for AI image generation] — include enough detail for DALL-E to create the diagram
- Title block must be single-spaced (one line per field, no blank lines between them)
- Key Vocabulary tables: Term | Definition format, no asterisks

Please create the booklet now, following the Prompt System v1.1 framework exactly. Save as a .docx file."""

    return prompt
