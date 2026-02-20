"""
Claude API integration for automated booklet generation.

Sends the master prompt to Claude and receives the generated booklet content.
Includes markdown sanitisation, .docx conversion with full formatting,
DALL-E diagram integration, and PDF export.
"""

import logging
import os
import re
import time
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from dotenv import load_dotenv

import anthropic

load_dotenv(override=True)

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "output"

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — comprehensive formatting instructions for Claude
# ---------------------------------------------------------------------------

DEFAULT_SYSTEM_PROMPT_CONTEXT = "AQA GCSE Combined Science: Trilogy (8464)"

SYSTEM_PROMPT_TEMPLATE = """You are a specialist educational content creator producing self-study
booklets for {course_context}.

LANGUAGE: You MUST use UK English spellings throughout the entire booklet.
Examples: organise (not organize), colour (not color), centre (not center),
analyse (not analyze), labelled (not labeled), modelling (not modeling),
specialise (not specialize), defence (not defense), fibre (not fiber),
travelled (not traveled), minimise (not minimize), recognise (not recognize).
No section is exempt from this rule.

CRITICAL FORMATTING RULES — you MUST follow every one of these:

1. NEVER use double asterisks (**) anywhere in your output.  All emphasis
   must be conveyed through section headings or plain text — we apply bold
   formatting during docx conversion.  Using ** will break the pipeline.

2. STRUCTURE — every booklet must contain these sections IN ORDER:
   a. Title block (single-spaced, one line per field):
      Self-Study Booklet
      Subject: [Subject]
      Topic: [Topic]
      Specification Reference: [Ref]
      Lesson Number: [Number] (Year [Year])
      Lesson Title: [Title]
      Required Practical: [Yes/No — name if applicable]

   b. Section 1 — Holistic Recall Starter (20 questions, numbered 1-20)
   c. Section 2 — Key Vocabulary Table (Term | Definition)
   d. Section 3 — Knowledge Development (per chunk, see below)
   e. Section 4 — Drawing and Labelling (if applicable)
   f. Section 5 — Calculations / Application Questions (numbered starting at 1)
   g. Section 6 — Summary / Key Takeaways (bullet points)
   h. Section 7 — Sentence Starters / Writing Frames (bullet points to help
      students structure written answers, e.g. "The function of the mitochondria is…")
   i. Section 8 — Mark Scheme (numbering restarts per section — see below)
   j. Section 9 — Self-Assessment / Progress Grid (RAG rating)
   k. Section 10 — Topics to Revisit (numbered 1, 2, 3 only)
   l. Section 11 — Targets for Next Lesson (numbered 1, 2, 3 only)
   m. Section 12 — Self-Assessment Actions (checkboxes)
   n. Section 13 — Document Info (version, date, page count)

3. KNOWLEDGE CHUNKS (Section 3) — create 3-5 chunks, each containing:
   - Introduction paragraph
   - Key Vocabulary table
   - Knowledge Content — BULLET POINTS ONLY (use - prefix), NEVER numbered
   - Worked Example — BULLET POINTS ONLY, NEVER numbered
   - Misconception box
   - Knowledge Check Questions — numbered starting at 1 for EACH chunk
     (Chunk 2 questions start at 1, NOT continuing from Chunk 1)

4. UNIVERSAL NUMBERING RESTART RULE: Every distinct numbered section MUST
   start its own numbering at 1.  No numbered section should EVER continue
   numbering from a previous section.  This applies to:
   - Knowledge Check Questions (restart at 1 per chunk)
   - Application Questions (start at 1)
   - Section 9: Topics to Revisit (1, 2, 3)
   - Section 10: Targets for Next Lesson (1, 2, 3)
   The ONLY exception is the Holistic Recall Starter (1-20 continuous).

5. MARK SCHEME (Section 7) — numbering MUST match the question numbering:
   Knowledge Chunk 1 — Mark Scheme:  1, 2, 3 …
   Knowledge Chunk 2 — Mark Scheme:  1, 2, 3 …  (restart, do NOT continue)
   Application Questions — Mark Scheme:  1, 2, 3 …  (restart, do NOT continue)
   If Q3 asks about magnification, mark scheme entry 3 MUST be about magnification.

6. DRAWING SPACES — wherever a diagram should go, output EXACTLY:
   [DRAWING SPACE: detailed description of what should be drawn]
   Include enough detail for an AI image generator to create the diagram.
   For the magnification triangle: [DRAWING SPACE: Magnification triangle showing I = A x M]
   For microscope: [DRAWING SPACE: Labelled diagram of a light microscope showing eyepiece, objective lenses, stage, mirror, and focusing knobs]

7. Use tables where appropriate (vocabulary, mark schemes, self-assessment).
8. Clearly mark Higher-Tier-only content with [HT ONLY] tags.
9. Target both Foundation and Higher tier.
10. Assume standard KS3 prior knowledge plus content from preceding lessons.

Output the complete booklet in well-structured markdown with clear
section headers using # for main sections and ## / ### for subsections."""


def get_system_prompt(course_config=None):
    """Build the system prompt, customised for the active course."""
    if course_config:
        context = course_config.get(
            "system_prompt_context", DEFAULT_SYSTEM_PROMPT_CONTEXT
        )
    else:
        context = DEFAULT_SYSTEM_PROMPT_CONTEXT
    return SYSTEM_PROMPT_TEMPLATE.format(course_context=context)


# Keep backwards-compatible reference for any existing imports
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(
    course_context=DEFAULT_SYSTEM_PROMPT_CONTEXT
)


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------

def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Add it to .env file. "
            "Get a key from console.anthropic.com"
        )
    return anthropic.Anthropic(api_key=api_key)


def generate_booklet(lesson, prompt_text, model="claude-sonnet-4-5-20250929",
                     course_config=None):
    """
    Send a booklet generation request to Claude API.

    Uses prompt caching on the system prompt to save ~90% on input tokens
    across multiple booklet generations (the system prompt is identical
    for all booklets in a course).

    Model selection: Sonnet 4.5 is the optimal choice — same price as
    Sonnet 4 ($3/$15 per MTok) but higher quality output. Haiku would
    risk lower quality on complex structured content. Opus is overkill
    for templated generation.
    """
    client = get_client()
    start = time.time()

    system_prompt = get_system_prompt(course_config)

    message = client.messages.create(
        model=model,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": prompt_text}],
    )

    duration = time.time() - start
    content = ""
    for block in message.content:
        if block.type == "text":
            content += block.text

    # Extract cache performance info
    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    # Include cache hit info if available
    if hasattr(message.usage, "cache_creation_input_tokens"):
        usage["cache_creation_input_tokens"] = message.usage.cache_creation_input_tokens
    if hasattr(message.usage, "cache_read_input_tokens"):
        usage["cache_read_input_tokens"] = message.usage.cache_read_input_tokens

    return {
        "content": content,
        "usage": usage,
        "model": message.model,
        "duration_s": round(duration, 1),
        "stop_reason": message.stop_reason,
    }


# ---------------------------------------------------------------------------
# Markdown sanitisation
# ---------------------------------------------------------------------------

def sanitize_markdown(content):
    """
    Post-process Claude's markdown to guarantee formatting compliance.
    Applied BEFORE docx conversion.

    Handles:
    - Stripping all ** markers
    - Forcing bullets in knowledge_content / worked_example sections
    - Restarting numbering in ALL numbered sections (universal rule)
    - UK English spelling corrections
    - Cleaning drawing space markers
    """
    # --- UK English corrections (applied globally) ---
    content = _fix_uk_english(content)

    lines = content.split("\n")
    result = []
    in_section = None  # track which section we're in
    q_counter = 0

    for line in lines:
        stripped = line.strip()

        # --- Detect current section from headings ---
        # NOTE: Order matters! More specific matches (mark scheme, knowledge check)
        # must come BEFORE broader matches (knowledge chunk) to handle headings
        # like "Knowledge Chunk 2 — Mark Scheme" correctly.
        heading_lower = stripped.lstrip("#").strip().lower()
        if stripped.startswith("#"):
            if "mark scheme" in heading_lower:
                # Must be checked before "knowledge chunk" since headings like
                # "Knowledge Chunk 2 — Mark Scheme" contain both
                in_section = "mark_scheme"
                q_counter = 0
            elif any(kw in heading_lower for kw in [
                "knowledge content", "key components", "key points",
                "knowledge development"
            ]):
                in_section = "knowledge_content"
            elif "worked example" in heading_lower:
                in_section = "worked_example"
            elif "knowledge check" in heading_lower:
                in_section = "knowledge_check"
                q_counter = 0
            elif any(kw in heading_lower for kw in [
                "application question", "calculation"
            ]):
                in_section = "application_questions"
                q_counter = 0
            elif any(kw in heading_lower for kw in [
                "topics to revisit", "topics for revisit"
            ]):
                in_section = "topics_to_revisit"
                q_counter = 0
            elif any(kw in heading_lower for kw in [
                "targets for next", "next lesson target"
            ]):
                in_section = "targets_next_lesson"
                q_counter = 0
            elif any(kw in heading_lower for kw in [
                "knowledge chunk", "chunk "
            ]):
                # New chunk resets question counter
                q_counter = 0
                in_section = None
            else:
                in_section = None

        # --- Strip all ** markers ---
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)

        # --- Force bullets in knowledge_content and worked_example ---
        if in_section in ("knowledge_content", "worked_example"):
            m = re.match(r"^(\s*)\d+\.\s+(.+)", line)
            if m:
                line = f"{m.group(1)}- {m.group(2)}"

        # --- Universal numbering restart for all numbered sections ---
        if in_section in (
            "knowledge_check", "application_questions",
            "topics_to_revisit", "targets_next_lesson",
            "mark_scheme"
        ):
            m = re.match(r"^(\s*)\d+\.\s+(.+)", line)
            if m:
                q_counter += 1
                line = f"{m.group(1)}{q_counter}. {m.group(2)}"

        # --- Clean drawing space markers ---
        # Keep the description for diagram generation, but standardise format
        m = re.match(r"^\[DRAWING\s+SPACE[:\s]*(.*)?\]$", stripped, re.IGNORECASE)
        if m:
            desc = (m.group(1) or "").strip().rstrip("]")
            if desc:
                line = f"[DRAWING SPACE: {desc}]"
            else:
                line = "[DRAWING SPACE]"

        result.append(line)

    return "\n".join(result)


# Common US → UK English spelling substitutions for science booklets
_UK_SPELLING_FIXES = [
    # -ize → -ise
    (r"\borganize\b", "organise"), (r"\bOrganize\b", "Organise"),
    (r"\borganized\b", "organised"), (r"\bOrganized\b", "Organised"),
    (r"\borganizing\b", "organising"), (r"\bOrganizing\b", "Organising"),
    (r"\brecognize\b", "recognise"), (r"\bRecognize\b", "Recognise"),
    (r"\brecognized\b", "recognised"), (r"\bRecognized\b", "Recognised"),
    (r"\brecognizing\b", "recognising"), (r"\bRecognizing\b", "Recognising"),
    (r"\bminimize\b", "minimise"), (r"\bMinimize\b", "Minimise"),
    (r"\bminimized\b", "minimised"), (r"\bminimizing\b", "minimising"),
    (r"\bmaximize\b", "maximise"), (r"\bMaximize\b", "Maximise"),
    (r"\bmaximized\b", "maximised"), (r"\bmaximizing\b", "maximising"),
    (r"\bspecialize\b", "specialise"), (r"\bSpecialize\b", "Specialise"),
    (r"\bspecialized\b", "specialised"), (r"\bSpecialized\b", "Specialised"),
    (r"\bspecializing\b", "specialising"),
    (r"\butilize\b", "utilise"), (r"\bUtilize\b", "Utilise"),
    (r"\butilized\b", "utilised"), (r"\butilizing\b", "utilising"),
    (r"\banalyze\b", "analyse"), (r"\bAnalyze\b", "Analyse"),
    (r"\banalyzed\b", "analysed"), (r"\banalyzing\b", "analysing"),
    (r"\bsummarize\b", "summarise"), (r"\bSummarize\b", "Summarise"),
    (r"\bsummarized\b", "summarised"), (r"\bsummarizing\b", "summarising"),
    (r"\bmemorize\b", "memorise"), (r"\bMemorize\b", "Memorise"),
    (r"\bmemorized\b", "memorised"), (r"\bmemorizing\b", "memorising"),
    (r"\bvaporize\b", "vaporise"), (r"\bvaporization\b", "vaporisation"),
    (r"\bneutralize\b", "neutralise"), (r"\bneutralized\b", "neutralised"),
    (r"\bneutralizing\b", "neutralising"), (r"\bneutralization\b", "neutralisation"),
    (r"\boxidize\b", "oxidise"), (r"\boxidized\b", "oxidised"),
    (r"\boxidizing\b", "oxidising"),
    (r"\bcauterize\b", "cauterise"), (r"\bcauterized\b", "cauterised"),
    (r"\bionize\b", "ionise"), (r"\bionized\b", "ionised"),
    (r"\bionizing\b", "ionising"), (r"\bionization\b", "ionisation"),
    (r"\bpolymerize\b", "polymerise"), (r"\bpolymerized\b", "polymerised"),
    (r"\bpolymerization\b", "polymerisation"),
    (r"\bcatalyze\b", "catalyse"), (r"\bcatalyzed\b", "catalysed"),
    (r"\bcatalyzing\b", "catalysing"),
    (r"\bhydrolyze\b", "hydrolyse"), (r"\bhydrolyzed\b", "hydrolysed"),
    (r"\bhydrolyzing\b", "hydrolysing"), (r"\bhydrolysis\b", "hydrolysis"),
    (r"\bcustomize\b", "customise"), (r"\bcustomized\b", "customised"),
    # -or → -our
    (r"\bcolor\b", "colour"), (r"\bColor\b", "Colour"),
    (r"\bcolors\b", "colours"), (r"\bColors\b", "Colours"),
    (r"\bcolored\b", "coloured"),
    (r"\bfavor\b", "favour"), (r"\bFavor\b", "Favour"),
    (r"\bfavored\b", "favoured"), (r"\bfavoring\b", "favouring"),
    (r"\bfavorite\b", "favourite"), (r"\bFavorite\b", "Favourite"),
    (r"\bhonor\b", "honour"), (r"\bHonor\b", "Honour"),
    (r"\bhumor\b", "humour"), (r"\bHumor\b", "Humour"),
    (r"\bbehavior\b", "behaviour"), (r"\bBehavior\b", "Behaviour"),
    (r"\bbehaviors\b", "behaviours"),
    (r"\bneighbor\b", "neighbour"), (r"\bNeighbor\b", "Neighbour"),
    (r"\bneighbors\b", "neighbours"),
    (r"\blabor\b", "labour"), (r"\bLabor\b", "Labour"),
    (r"\bvapor\b", "vapour"), (r"\bVapor\b", "Vapour"),
    (r"\btumor\b", "tumour"), (r"\bTumor\b", "Tumour"),
    (r"\bodor\b", "odour"), (r"\bOdor\b", "Odour"),
    # -er → -re
    (r"\bcenter\b", "centre"), (r"\bCenter\b", "Centre"),
    (r"\bcenters\b", "centres"), (r"\bCenters\b", "Centres"),
    (r"\bcentered\b", "centred"),
    (r"\bfiber\b", "fibre"), (r"\bFiber\b", "Fibre"),
    (r"\bfibers\b", "fibres"),
    (r"\bliter\b", "litre"), (r"\bLiter\b", "Litre"),
    (r"\bliters\b", "litres"),
    (r"\bmeter\b", "metre"), (r"\bMeter\b", "Metre"),
    (r"\bmeters\b", "metres"),
    # -ed / -ing / -ling
    (r"\blabeled\b", "labelled"), (r"\bLabeled\b", "Labelled"),
    (r"\blabeling\b", "labelling"), (r"\bLabeling\b", "Labelling"),
    (r"\bmodeled\b", "modelled"), (r"\bModeled\b", "Modelled"),
    (r"\bmodeling\b", "modelling"), (r"\bModeling\b", "Modelling"),
    (r"\btraveled\b", "travelled"), (r"\btraveling\b", "travelling"),
    (r"\bcanceled\b", "cancelled"), (r"\bcanceling\b", "cancelling"),
    # -ence / -ense
    (r"\bdefense\b", "defence"), (r"\bDefense\b", "Defence"),
    (r"\boffense\b", "offence"), (r"\bOffense\b", "Offence"),
    (r"\blicense\b", "licence"), (r"\bLicense\b", "Licence"),
    (r"\bpractice\b(?=\s+(?:the|this|that|a|an))", "practise"),  # verb form only
    # Other common differences
    (r"\bgray\b", "grey"), (r"\bGray\b", "Grey"),
    (r"\bgrays\b", "greys"),
    (r"\bfetus\b", "foetus"), (r"\bFetus\b", "Foetus"),
    (r"\besophagus\b", "oesophagus"), (r"\bEsophagus\b", "Oesophagus"),
    (r"\bestrogen\b", "oestrogen"), (r"\bEstrogen\b", "Oestrogen"),
    (r"\bhemoglobin\b", "haemoglobin"), (r"\bHemoglobin\b", "Haemoglobin"),
    (r"\banemia\b", "anaemia"), (r"\bAnemia\b", "Anaemia"),
    (r"\bdiarrhea\b", "diarrhoea"), (r"\bDiarrhea\b", "Diarrhoea"),
    (r"\bpediatrician\b", "paediatrician"),
    (r"\bsulfur\b", "sulphur"), (r"\bSulfur\b", "Sulphur"),
    (r"\bsulfate\b", "sulphate"), (r"\bSulfate\b", "Sulphate"),
    (r"\bsulfide\b", "sulphide"), (r"\bSulfide\b", "Sulphide"),
    (r"\bsulfuric\b", "sulphuric"), (r"\bSulfuric\b", "Sulphuric"),
    (r"\baluminum\b", "aluminium"), (r"\bAluminum\b", "Aluminium"),
]


def _fix_uk_english(text):
    """Apply UK English spelling corrections to text."""
    for pattern, replacement in _UK_SPELLING_FIXES:
        text = re.sub(pattern, replacement, text)
    return text


# ---------------------------------------------------------------------------
# Markdown → Docx conversion
# ---------------------------------------------------------------------------

def _set_cell_border(cell, **kwargs):
    """Set border on a table cell.  kwargs: top, bottom, left, right each a dict."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge, attrs in kwargs.items():
        el = OxmlElement(f"w:{edge}")
        for k, v in attrs.items():
            el.set(qn(f"w:{k}"), str(v))
        tcBorders.append(el)
    tcPr.append(tcBorders)


def _add_page_number(paragraph):
    """Insert a PAGE field into a paragraph (for footer)."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    run._r.append(fldChar1)

    run2 = paragraph.add_run()
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = " PAGE "
    run2._r.append(instrText)

    run3 = paragraph.add_run()
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run3._r.append(fldChar2)


def markdown_to_docx(md_path, lesson=None, diagram_images=None):
    """
    Convert a markdown booklet to .docx with full formatting.

    Args:
        md_path: path to the .md file
        lesson: lesson dict (optional, for header/footer)
        diagram_images: dict mapping drawing-space descriptions to image paths
    """
    md_path = Path(md_path)
    content = md_path.read_text()
    diagram_images = diagram_images or {}

    doc = Document()

    # --- Document setup ---
    # Margins: 2.54 cm (1 inch) all sides
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

    # Header — lesson title
    if lesson:
        header = doc.sections[0].header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        hr = hp.add_run(lesson.get("title", ""))
        hr.font.size = Pt(9)
        hr.font.color.rgb = RGBColor(128, 128, 128)
        hr.font.name = "Calibri"

    # Footer — page numbers
    footer = doc.sections[0].footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_page_number(fp)

    # Default font
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    # Heading styles
    for level, size in [(1, 14), (2, 13), (3, 12), (4, 11)]:
        hstyle = doc.styles[f"Heading {level}"]
        hstyle.font.name = "Calibri"
        hstyle.font.size = Pt(size)
        hstyle.font.bold = True
        hstyle.font.color.rgb = RGBColor(0x1D, 0x1D, 0x1F)

    # --- Parse and build document ---
    lines = content.split("\n")
    i = 0
    in_table = False
    table_rows = []
    in_title_block = False
    current_section = None  # track section for context-aware formatting

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # --- Headings ---
        if stripped.startswith("####"):
            text = stripped[4:].strip()
            doc.add_heading(text, level=4)
            current_section = _detect_section(text)
            i += 1
            continue
        elif stripped.startswith("###"):
            text = stripped[3:].strip()
            doc.add_heading(text, level=3)
            current_section = _detect_section(text)
            i += 1
            continue
        elif stripped.startswith("##"):
            text = stripped[2:].strip()
            doc.add_heading(text, level=2)
            current_section = _detect_section(text)
            i += 1
            continue
        elif stripped.startswith("#"):
            text = stripped.lstrip("#").strip()
            h = doc.add_heading(text, level=1)
            current_section = _detect_section(text)
            # Detect title block start
            if "self-study booklet" in text.lower():
                in_title_block = True
            i += 1
            continue

        # --- Title block: single line spacing ---
        if in_title_block:
            if stripped == "" or stripped.startswith("#"):
                in_title_block = False
            else:
                p = doc.add_paragraph()
                pf = p.paragraph_format
                pf.space_before = Pt(0)
                pf.space_after = Pt(0)
                # Bold label, regular value
                if ":" in stripped:
                    label, _, value = stripped.partition(":")
                    run_label = p.add_run(label + ":")
                    run_label.bold = True
                    run_label.font.name = "Calibri"
                    run_label.font.size = Pt(11)
                    run_value = p.add_run(" " + value.strip())
                    run_value.font.name = "Calibri"
                    run_value.font.size = Pt(11)
                else:
                    _add_formatted_text(p, stripped)
                i += 1
                continue

        # --- Table detection ---
        if stripped.startswith("|") and "|" in stripped[1:]:
            if not in_table:
                in_table = True
                table_rows = []
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            # Skip separator rows (|---|---|)
            if cells and not all(set(c) <= set("-: ") for c in cells):
                # Strip any residual ** from cell text
                cells = [re.sub(r"\*\*([^*]+)\*\*", r"\1", c) for c in cells]
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            in_table = False
            if table_rows:
                _render_table(doc, table_rows)
            # Don't skip — process this line normally

        # --- Horizontal rule ---
        if stripped in ("---", "***", "___"):
            p = doc.add_paragraph()
            p.add_run("_" * 60)
            i += 1
            continue

        # --- Drawing space ---
        ds_match = re.match(
            r"^\[DRAWING\s+SPACE(?:[:\s]*(.+?))?\]$", stripped, re.IGNORECASE
        )
        if ds_match:
            desc = (ds_match.group(1) or "").strip()
            # Check if we have a generated diagram image
            img_path = _find_diagram_image(desc, diagram_images)

            if img_path and Path(img_path).exists():
                # Embed diagram image — 4 inches wide to fit within margins
                try:
                    doc.add_picture(str(img_path), width=Inches(4.0))
                    last_para = doc.paragraphs[-1]
                    last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                except Exception as e:
                    logger.warning(f"Failed to embed diagram: {e}")
                    _add_drawing_box(doc, desc, error=True)
            else:
                # Empty bordered box with error placeholder if DALL-E was expected
                has_openai = bool(os.getenv("OPENAI_API_KEY"))
                _add_drawing_box(doc, desc, error=has_openai)
            i += 1
            continue

        # --- Bullet points ---
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:]
            p = doc.add_paragraph(style="List Bullet")
            _add_formatted_text(p, text)
            i += 1
            continue

        # --- Numbered list ---
        num_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if num_match:
            # Context-aware: force bullets in knowledge content / worked example
            if current_section in ("knowledge_content", "worked_example"):
                p = doc.add_paragraph(style="List Bullet")
                _add_formatted_text(p, num_match.group(2))
            else:
                p = doc.add_paragraph(style="List Number")
                _add_formatted_text(p, num_match.group(2))
                # Add answer space after knowledge check and application questions
                if current_section in ("knowledge_check", "application_questions"):
                    for _ in range(5):
                        blank = doc.add_paragraph()
                        blank.paragraph_format.space_before = Pt(0)
                        blank.paragraph_format.space_after = Pt(0)
            i += 1
            continue

        # --- Empty line ---
        if not stripped:
            doc.add_paragraph()
            i += 1
            continue

        # --- Regular paragraph ---
        p = doc.add_paragraph()
        _add_formatted_text(p, stripped)
        i += 1

    # Handle any remaining table
    if in_table and table_rows:
        _render_table(doc, table_rows)

    # Save
    docx_path = md_path.with_suffix(".docx")
    doc.save(str(docx_path))
    return str(docx_path)


def _detect_section(heading_text):
    """Detect which section we're in from a heading."""
    h = heading_text.lower()
    if any(kw in h for kw in [
        "knowledge content", "key components", "key points",
        "knowledge development"
    ]):
        return "knowledge_content"
    if "worked example" in h:
        return "worked_example"
    if "knowledge check" in h:
        return "knowledge_check"
    if any(kw in h for kw in ["application question", "calculation"]):
        return "application_questions"
    if any(kw in h for kw in ["topics to revisit", "topics for revisit"]):
        return "topics_to_revisit"
    if any(kw in h for kw in ["targets for next", "next lesson target"]):
        return "targets_next_lesson"
    if "mark scheme" in h:
        return "mark_scheme"
    return None


def _render_table(doc, table_rows):
    """Render a markdown-parsed table into the document."""
    num_cols = max(len(r) for r in table_rows)
    table = doc.add_table(rows=len(table_rows), cols=num_cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for r_idx, row_data in enumerate(table_rows):
        for c_idx, cell_text in enumerate(row_data):
            if c_idx < num_cols:
                cell = table.cell(r_idx, c_idx)
                cell.text = ""
                p = cell.paragraphs[0]
                _add_formatted_text(p, cell_text)
                # Bold header row
                if r_idx == 0:
                    for run in p.runs:
                        run.bold = True
                        run.font.name = "Calibri"
                        run.font.size = Pt(11)

    doc.add_paragraph()  # spacing after table


def _find_diagram_image(description, diagram_images):
    """
    Find a matching diagram image for a drawing space description.

    Tries multiple matching strategies:
    1. Exact match
    2. Case-insensitive containment (either direction)
    3. Significant word overlap
    """
    if not description or not diagram_images:
        return None

    desc_lower = description.lower().strip()

    # 1. Exact match
    if description in diagram_images:
        return diagram_images[description]

    # 2. Case-insensitive containment
    for key, path in diagram_images.items():
        key_lower = key.lower().strip()
        if desc_lower in key_lower or key_lower in desc_lower:
            return path

    # 3. Significant word overlap (at least 3 shared words)
    desc_words = set(re.findall(r"\w{3,}", desc_lower))
    for key, path in diagram_images.items():
        key_words = set(re.findall(r"\w{3,}", key.lower()))
        overlap = desc_words & key_words
        if len(overlap) >= 3:
            return path

    return None


def _add_drawing_box(doc, description="", error=False):
    """
    Add a bordered box for drawing space.

    If error=True, adds a placeholder message indicating image generation
    failed — the user should regenerate the booklet.
    """
    # Use a 1-cell table with generous height
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    cell = table.cell(0, 0)
    cell.text = ""

    if error:
        # Add error placeholder text
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("[Image generation failed — regenerate this booklet]")
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(180, 0, 0)
        run.font.name = "Calibri"
        run.italic = True

    # Set minimum height (~4 inches / ~10cm)
    tr = cell._tc.getparent()
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement("w:trHeight")
    trHeight.set(qn("w:val"), "5760")  # ~4 inches in twips
    trHeight.set(qn("w:hRule"), "atLeast")
    trPr.append(trHeight)

    # Set cell width to full page width
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = OxmlElement("w:tcW")
    tcW.set(qn("w:w"), "9360")  # ~6.5 inches
    tcW.set(qn("w:type"), "dxa")
    tcPr.append(tcW)

    doc.add_paragraph()  # spacing after box


def _add_formatted_text(paragraph, text):
    """Parse inline markdown formatting and add runs to paragraph."""
    # Strip any residual ** from text
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

    # Split on italic (*text*) and code (`text`) patterns
    parts = re.split(r"(\*[^*]+\*|`[^`]+`)", text)
    for part in parts:
        if part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
            run.font.name = "Calibri"
            run.font.size = Pt(11)
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Courier New"
            run.font.size = Pt(10)
        elif part:
            run = paragraph.add_run(part)
            run.font.name = "Calibri"
            run.font.size = Pt(11)


# ---------------------------------------------------------------------------
# File naming & existence checks
# ---------------------------------------------------------------------------

def _build_filename(lesson, ext=".md"):
    """Build the standardised filename, including RP code if applicable."""
    num = lesson["lesson_number"]
    title = lesson["title"] or "Untitled"
    rp = lesson.get("required_practical") or ""

    # Only prepend RP code if title doesn't already start with it
    if rp and rp.lower() not in ("none", "n/a", "") and not title.lower().startswith(rp.lower()):
        fname = f"L{num:03d} - {rp} - {title}{ext}"
    else:
        fname = f"L{num:03d} - {title}{ext}"

    return fname.replace("/", "-").replace(":", " -")


def _build_output_dir(lesson):
    """Build and return the output directory for a lesson."""
    topic_folder = lesson.get("output_folder", "").rstrip("/")
    subject = lesson["subject"] or "Unknown"
    out_dir = OUTPUT_DIR / topic_folder if topic_folder else OUTPUT_DIR / subject
    return out_dir


def check_existing_booklet(lesson):
    """Check if a booklet already exists for this lesson."""
    out_dir = _build_output_dir(lesson)
    docx_name = _build_filename(lesson, ".docx")
    pdf_name = _build_filename(lesson, ".pdf")

    docx_path = out_dir / docx_name
    pdf_path = out_dir / pdf_name

    # Also check old naming convention (without RP code)
    old_docx = out_dir / f"L{lesson['lesson_number']:03d} - {lesson['title']}.docx".replace("/", "-").replace(":", " -")

    exists = docx_path.exists() or old_docx.exists()

    return {
        "exists": exists,
        "docx_path": str(docx_path if docx_path.exists() else old_docx),
        "pdf_path": str(pdf_path),
    }


# ---------------------------------------------------------------------------
# Save markdown
# ---------------------------------------------------------------------------

def save_booklet_markdown(lesson, content):
    """Save generated content as markdown file in output directory."""
    out_dir = _build_output_dir(lesson)
    out_dir.mkdir(parents=True, exist_ok=True)

    fname = _build_filename(lesson, ".md")
    fpath = out_dir / fname
    fpath.write_text(content)
    return str(fpath)


# ---------------------------------------------------------------------------
# PDF conversion
# ---------------------------------------------------------------------------

def convert_to_pdf(docx_path):
    """
    Convert a .docx to .pdf using LibreOffice.

    Falls back to docx2pdf (which needs MS Word) if LibreOffice isn't available.
    Returns pdf path or None on failure.
    """
    import shutil
    import subprocess

    docx_path = Path(docx_path)
    pdf_path = docx_path.with_suffix(".pdf")

    # Strategy 1: LibreOffice (free, works on Mac/Linux/Windows)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        try:
            result = subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(docx_path.parent),
                    str(docx_path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if pdf_path.exists():
                logger.info(f"PDF created via LibreOffice: {pdf_path}")
                return str(pdf_path)
            else:
                logger.warning(f"LibreOffice conversion produced no file. stderr: {result.stderr}")
        except Exception as e:
            logger.warning(f"LibreOffice conversion failed: {e}")

    # Strategy 2: docx2pdf (needs MS Word on Mac)
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        if pdf_path.exists():
            return str(pdf_path)
    except Exception as e:
        logger.warning(f"docx2pdf conversion failed: {e}")

    logger.warning("PDF conversion failed — install LibreOffice or MS Word")
    return None


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def generate_and_save(lesson, prompt_text, model="claude-sonnet-4-5-20250929",
                      replace=False, course_config=None):
    """
    Full pipeline: generate via API → sanitise → diagrams → docx → pdf.

    Args:
        lesson: lesson dict from parser
        prompt_text: the master prompt
        model: Claude model to use
        replace: if True, overwrite existing files
        course_config: optional course config dict

    Returns dict with paths and metadata.
    """
    # Check for existing files
    existing = check_existing_booklet(lesson)
    if existing["exists"] and not replace:
        raise FileExistsError(
            f"Booklet already exists at {existing['docx_path']}. "
            "Set replace=True to overwrite."
        )

    # Generate via Claude API
    result = generate_booklet(
        lesson, prompt_text, model=model, course_config=course_config
    )

    # Sanitise the markdown
    clean_content = sanitize_markdown(result["content"])

    # Save markdown
    md_path = save_booklet_markdown(lesson, clean_content)

    # Generate diagrams via Claude SVG (preferred) or DALL-E (fallback)
    diagram_images = {}
    try:
        from svg_diagrams import generate_diagrams_for_booklet as svg_generate
        out_dir = _build_output_dir(lesson)
        diagram_images = svg_generate(clean_content, str(out_dir))
    except Exception as e:
        logger.warning(f"SVG diagram generation failed, trying DALL-E: {e}")
        try:
            from diagrams import generate_diagrams_for_booklet as dalle_generate
            out_dir = _build_output_dir(lesson)
            diagram_images = dalle_generate(clean_content, str(out_dir))
        except Exception as e2:
            logger.warning(f"Diagram generation skipped: {e2}")

    # Convert to docx
    docx_path = markdown_to_docx(md_path, lesson=lesson, diagram_images=diagram_images)

    # Convert to PDF
    pdf_path = convert_to_pdf(docx_path)

    return {
        "md_path": md_path,
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "usage": result["usage"],
        "model": result["model"],
        "duration_s": result["duration_s"],
        "stop_reason": result["stop_reason"],
    }
