"""
Claude API integration for automated booklet generation.

Sends the master prompt to Claude and receives the generated booklet content.
Claude returns the booklet as a .docx artifact which we save to disk.
"""

import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from docx.shared import Pt, Inches, RGBColor

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "output"

# System prompt matching the Claude Project instructions from the production guide
SYSTEM_PROMPT = """You are a specialist educational content creator producing self-study
booklets for AQA GCSE Combined Science: Trilogy (8464).

For every booklet you create, you MUST:

1. Follow the Self-Study Booklet Prompt System v1.1 exactly
2. Use the scheme of work for lesson sequencing and content scope
3. Reference the AQA specification for accurate content
4. Produce well-structured content suitable for a .docx file
5. Target both Foundation and Higher tier (HT content flagged)
6. Assume standard KS3 prior knowledge plus content from any preceding lessons in the scheme of work
7. Apply ALL updated rules: question-content alignment, drawing space for diagrams, and self-correction task completion

Structure every booklet with:
- Cover page (subject, topic, spec ref, lesson number)
- 20 one-word holistic recall starter + answer key
- 3-5 knowledge chunks (each with vocabulary, knowledge, worked example, misconception box, 6+ knowledge check questions)
- Summary box
- Sentence starters panel
- 8 exam-style questions (escalating difficulty)
- Full mark schemes (recall, knowledge checks, exam Qs with Grade 4/7/9 exemplars)
- Self-assessment grid with score calculator

Output the complete booklet content in well-structured markdown with clear section headers.
Use tables where appropriate (for mark schemes, self-assessment grids).
Clearly mark HT-only content with [HT ONLY] tags.
Include placeholder notes like [DRAWING SPACE: description] where diagrams should go."""


def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Add it to .env file. "
            "Get a key from console.anthropic.com"
        )
    return anthropic.Anthropic(api_key=api_key)


def generate_booklet(lesson, prompt_text, model="claude-sonnet-4-5-20250929"):
    """
    Send a booklet generation request to Claude API.

    Args:
        lesson: lesson dict from parser
        prompt_text: the master prompt from prompt_generator
        model: Claude model to use

    Returns:
        dict with keys:
            'content': the generated markdown content
            'usage': token usage info
            'model': model used
            'duration_s': time taken
    """
    client = get_client()

    start = time.time()

    message = client.messages.create(
        model=model,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt_text}
        ],
    )

    duration = time.time() - start

    # Extract text content
    content = ""
    for block in message.content:
        if block.type == "text":
            content += block.text

    return {
        "content": content,
        "usage": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        },
        "model": message.model,
        "duration_s": round(duration, 1),
        "stop_reason": message.stop_reason,
    }


def save_booklet_markdown(lesson, content):
    """Save generated content as markdown file in output directory."""
    subject = lesson["subject"] or "Unknown"
    topic_code = re.match(r"([BCP]\d+)", lesson["topic"] or "")
    topic_folder = lesson.get("output_folder", "").rstrip("/")

    # Create output directory structure
    out_dir = OUTPUT_DIR / topic_folder if topic_folder else OUTPUT_DIR / subject
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save as markdown
    fname = f"L{lesson['lesson_number']:03d} - {lesson['title']}.md"
    fname = fname.replace("/", "-").replace(":", " -")
    fpath = out_dir / fname
    fpath.write_text(content)

    return str(fpath)


def markdown_to_docx(md_path):
    """
    Convert a markdown booklet to .docx format using python-docx.

    This creates a properly formatted Word document with:
    - Headers at appropriate levels
    - Tables for mark schemes and grids
    - Bold/italic formatting
    - Page-like structure
    """
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT

    md_path = Path(md_path)
    content = md_path.read_text()

    doc = Document()

    # Set default font
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    # Parse markdown and build document
    lines = content.split("\n")
    i = 0
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Headers
        if stripped.startswith("# ") and not stripped.startswith("## "):
            p = doc.add_heading(stripped[2:], level=1)
            i += 1
            continue
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
            i += 1
            continue
        elif stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
            i += 1
            continue
        elif stripped.startswith("#### "):
            doc.add_heading(stripped[5:], level=4)
            i += 1
            continue

        # Table detection
        if stripped.startswith("|") and "|" in stripped[1:]:
            if not in_table:
                in_table = True
                table_rows = []
            # Parse table row
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            # Skip separator rows (|---|---|)
            if cells and not all(set(c) <= set("-: ") for c in cells):
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            # End of table — render it
            in_table = False
            if table_rows:
                num_cols = max(len(r) for r in table_rows)
                table = doc.add_table(rows=len(table_rows), cols=num_cols)
                table.style = "Table Grid"
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row_data in enumerate(table_rows):
                    for c_idx, cell_text in enumerate(row_data):
                        if c_idx < num_cols:
                            cell = table.cell(r_idx, c_idx)
                            cell.text = cell_text
                            # Bold header row
                            if r_idx == 0:
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.bold = True
                doc.add_paragraph()  # spacing after table
                table_rows = []
            # Don't skip — process this line normally below

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            p = doc.add_paragraph()
            p.add_run("_" * 60)
            i += 1
            continue

        # Drawing space placeholder
        if stripped.startswith("[DRAWING SPACE"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped)
            run.italic = True
            run.font.color.rgb = RGBColor(128, 128, 128)
            # Add empty lines for space
            for _ in range(3):
                doc.add_paragraph()
            i += 1
            continue

        # Bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:]
            p = doc.add_paragraph(style="List Bullet")
            _add_formatted_text(p, text)
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s", "", stripped)
            p = doc.add_paragraph(style="List Number")
            _add_formatted_text(p, text)
            i += 1
            continue

        # Empty line
        if not stripped:
            doc.add_paragraph()
            i += 1
            continue

        # Regular paragraph with inline formatting
        p = doc.add_paragraph()
        _add_formatted_text(p, stripped)
        i += 1

    # Handle any remaining table
    if in_table and table_rows:
        num_cols = max(len(r) for r in table_rows)
        table = doc.add_table(rows=len(table_rows), cols=num_cols)
        table.style = "Table Grid"
        for r_idx, row_data in enumerate(table_rows):
            for c_idx, cell_text in enumerate(row_data):
                if c_idx < num_cols:
                    table.cell(r_idx, c_idx).text = cell_text

    # Save as .docx
    docx_path = md_path.with_suffix(".docx")
    doc.save(str(docx_path))
    return str(docx_path)


def _add_formatted_text(paragraph, text):
    """Parse inline markdown formatting and add runs to paragraph."""
    # Split on bold (**text**) and italic (*text*) patterns
    parts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Courier New"
            run.font.size = Pt(10)
        elif part:
            paragraph.add_run(part)


def generate_and_save(lesson, prompt_text, model="claude-sonnet-4-5-20250929"):
    """
    Full pipeline: generate via API, save markdown, convert to docx.

    Returns dict with paths and metadata.
    """
    # Generate
    result = generate_booklet(lesson, prompt_text, model=model)

    # Save markdown
    md_path = save_booklet_markdown(lesson, result["content"])

    # Convert to docx
    docx_path = markdown_to_docx(md_path)

    return {
        "md_path": md_path,
        "docx_path": docx_path,
        "usage": result["usage"],
        "model": result["model"],
        "duration_s": result["duration_s"],
        "stop_reason": result["stop_reason"],
    }
