"""
Scheme of Work Generator & Review Engine (Prompt Sheet 13).

Provides:
  - AI review of uploaded schemes against reference documents
  - AI generation of new schemes of work from scratch
  - Structured JSON storage of schemes
  - Apply-suggestion support for iterative improvement
"""

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)


def _extract_json(raw, expect_object=False):
    """Robustly extract JSON from AI response text."""
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
    raw = re.sub(r"\n?```\s*$", "", raw)
    if expect_object:
        start, end = raw.find("{"), raw.rfind("}")
    else:
        start, end = raw.find("["), raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw


def _repair_json(raw_text, expect_object=True):
    """Attempt to repair malformed JSON from AI responses.

    Handles:
    - Truncated output (missing closing brackets/braces)
    - Missing commas between elements
    - Single quotes instead of double quotes
    - Unquoted keys
    - Trailing commas (already handled by _extract_json)
    """
    text = _extract_json(raw_text, expect_object=expect_object)

    # First try: maybe it's already valid
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fix: missing commas between } { or ] [ or } [ or ] {
    text = re.sub(r'(\})\s*(\{)', r'\1,\2', text)
    text = re.sub(r'(\])\s*(\[)', r'\1,\2', text)
    text = re.sub(r'(\})\s*(\[)', r'\1,\2', text)
    text = re.sub(r'(\])\s*(\{)', r'\1,\2', text)

    # Fix: missing commas between "value" "key" patterns (string followed by string)
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)

    # Fix: missing comma after true/false/null/number before "key"
    text = re.sub(r'(true|false|null|\d)\s*\n\s*"', r'\1,\n"', text)

    # Second try after comma fixes
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fix truncated JSON: count brackets and close any unclosed ones
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')

    if open_braces > 0 or open_brackets > 0:
        # Truncated output — try progressively aggressive repairs

        # Strategy 1: Trim trailing partial content, then close brackets
        # using stack-based nesting order
        for trim_text in [text, text.rstrip().rstrip(',')]:
            # Try trimming back to the last complete value
            for trim_pattern in [
                r',\s*"[^"]*$',             # trailing partial key/string
                r',\s*"[^"]*":\s*"[^"]*$',  # trailing partial key:"value
                r',\s*"[^"]*":\s*\{[^}]*$', # trailing partial key:{obj
                r',\s*"[^"]*":\s*\[[^\]]*$',# trailing partial key:[arr
                r',\s*\{[^}]*$',            # trailing partial object in array
                r'',                         # no trim (try as-is)
            ]:
                if trim_pattern:
                    candidate = re.sub(trim_pattern, '', trim_text)
                else:
                    candidate = trim_text

                # Use stack to determine correct bracket close order
                stack = []
                in_string = False
                escape_next = False
                for ch in candidate:
                    if escape_next:
                        escape_next = False
                        continue
                    if ch == '\\' and in_string:
                        escape_next = True
                        continue
                    if ch == '"':
                        in_string = not in_string
                        continue
                    if in_string:
                        continue
                    if ch in '{[':
                        stack.append('}' if ch == '{' else ']')
                    elif ch in '}]':
                        if stack:
                            stack.pop()

                if stack:
                    candidate += ''.join(reversed(stack))

                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

    # If nothing worked, raise the original error for logging
    raise json.JSONDecodeError(
        f"Could not repair JSON ({open_braces} unclosed braces, {open_brackets} unclosed brackets)",
        text[:200], 0
    )


SCHEMES_DIR = Path(__file__).parent / "data" / "schemes"
SCHEMES_DIR.mkdir(parents=True, exist_ok=True)


# ───────────────────────────────────────────────────────────────────
# System prompts
# ───────────────────────────────────────────────────────────────────

SOW_REVIEW_SYSTEM_PROMPT = """You are a UK curriculum expert and school improvement specialist.
You review schemes of work against reference materials and provide detailed, constructive feedback.

RULES:
- Use UK English throughout.
- Be specific and actionable in every piece of feedback.
- Ground every suggestion in the reference materials provided.
- Be constructive — highlight strengths as well as improvements.
- When suggesting changes, be precise about where they should go.

OUTPUT: You MUST return valid JSON matching the schema described in the user prompt.
Do NOT wrap the JSON in markdown code fences. Return raw JSON only."""

SOW_GENERATE_SYSTEM_PROMPT = """You are a UK curriculum design expert who creates detailed, high-quality schemes of work.

RULES:
- Use UK English throughout.
- Follow the school's scheme of work format exactly if one is provided.
- Cover ALL required National Curriculum or specification content.
- Sequence lessons logically with appropriate progression.
- Include assessment points at regular intervals.
- Ensure appropriate pacing — not too fast, not too slow.
- Include key vocabulary for every unit/lesson.
- Include cross-curricular links where natural.

OUTPUT: You MUST return valid JSON matching the schema described in the user prompt.
Do NOT wrap the JSON in markdown code fences. Return raw JSON only."""

SOW_APPLY_SUGGESTION_PROMPT = """You are a UK curriculum expert modifying a scheme of work based on a specific suggestion.

RULES:
- Make ONLY the change described in the suggestion.
- Preserve all other content exactly as it is.
- Maintain consistent formatting and structure.
- If adding lessons, number them appropriately.
- If moving content, update all affected lesson numbers.
- Use UK English throughout.

OUTPUT: Return the COMPLETE modified scheme of work as valid JSON.
Do NOT wrap the JSON in markdown code fences. Return raw JSON only."""


def _get_client():
    """Get Anthropic client."""
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _create_message(**kwargs):
    """Create a message using streaming to avoid the 10-minute SDK timeout."""
    from ai_client import create_message
    return create_message(**kwargs)


def _scheme_path(scheme_id):
    return SCHEMES_DIR / f"{scheme_id}.json"


def _review_path(scheme_id):
    return SCHEMES_DIR / f"{scheme_id}_review.json"


# ───────────────────────────────────────────────────────────────────
# Scheme CRUD
# ───────────────────────────────────────────────────────────────────

def list_schemes(deduplicate=True):
    """List all saved schemes. When deduplicate=True, keeps only the latest
    version of each unique (title + subject + yearGroup) combination."""
    raw = []
    for p in sorted(SCHEMES_DIR.glob("*.json")):
        if p.stem.endswith("_review"):
            continue
        try:
            data = json.loads(p.read_text())
            raw.append({
                "id": data.get("id", p.stem),
                "subject": data.get("subject", ""),
                "key_stage": data.get("keyStage", data.get("key_stage", "")),
                "year_group": data.get("yearGroup", data.get("year_group", "")),
                "title": data.get("title", f"{data.get('subject', 'Unknown')} — Year {data.get('yearGroup', '?')}"),
                "total_lessons": data.get("totalLessons", 0),
                "exam_board": data.get("examBoard", data.get("exam_board", "")),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "source": data.get("source", ""),
                "has_review": _review_path(data.get("id", p.stem)).exists(),
                "file_path": str(p),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    if not deduplicate:
        return raw

    # Deduplicate: keep only the latest (by updated_at or created_at) per
    # unique (title, subject, year_group) key
    best = {}
    for s in raw:
        key = (s["title"].strip().lower(), s["subject"].strip().lower(),
               str(s["year_group"]).strip())
        ts = s.get("updated_at") or s.get("created_at") or ""
        if key not in best or ts > (best[key].get("updated_at") or best[key].get("created_at") or ""):
            best[key] = s
    return list(best.values())


def get_scheme(scheme_id):
    """Load a full scheme by ID."""
    path = _scheme_path(scheme_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_scheme(scheme_data):
    """Save a scheme (creates or updates)."""
    if "id" not in scheme_data or not scheme_data["id"]:
        scheme_data["id"] = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    if "created_at" not in scheme_data:
        scheme_data["created_at"] = now
    scheme_data["updated_at"] = now
    _scheme_path(scheme_data["id"]).write_text(json.dumps(scheme_data, indent=2))
    return scheme_data


def delete_scheme(scheme_id):
    """Delete a scheme and its review."""
    path = _scheme_path(scheme_id)
    if path.exists():
        path.unlink()
    review = _review_path(scheme_id)
    if review.exists():
        review.unlink()
    return True


def get_review(scheme_id):
    """Load review results for a scheme."""
    path = _review_path(scheme_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())


# ───────────────────────────────────────────────────────────────────
# Import from spreadsheet
# ───────────────────────────────────────────────────────────────────

def find_existing_scheme(title, subject, year_group):
    """Check if a scheme with the same title+subject+yearGroup already exists.
    Returns the existing scheme data (dict) or None."""
    title_lc = (title or "").strip().lower()
    subject_lc = (subject or "").strip().lower()
    yg_str = str(year_group).strip()
    for p in SCHEMES_DIR.glob("*.json"):
        if p.stem.endswith("_review"):
            continue
        try:
            data = json.loads(p.read_text())
            if (data.get("title", "").strip().lower() == title_lc
                    and data.get("subject", "").strip().lower() == subject_lc
                    and str(data.get("yearGroup", data.get("year_group", ""))).strip() == yg_str):
                return data
        except (json.JSONDecodeError, KeyError):
            continue
    return None


def import_from_course(course_config, parsed_data):
    """
    Convert existing course parsed data into a scheme of work JSON structure.
    This bridges the existing pipeline data to the scheme format.

    Deduplication: if a scheme with the same title+subject+yearGroup already
    exists, update it in-place rather than creating a new copy.
    """
    lessons = parsed_data.get("all_lessons", [])
    if not lessons:
        raise ValueError("No lessons found in parsed data")

    # Group by year, then by topic/unit
    by_year = {}
    for l in lessons:
        y = l.get("year", 0)
        by_year.setdefault(y, []).append(l)

    # Build terms/units structure
    terms = []
    for year in sorted(by_year.keys()):
        year_lessons = sorted(by_year[year], key=lambda x: x.get("lesson_number", 0))

        # Group by topic
        units = []
        current_topic = None
        current_unit_lessons = []

        for l in year_lessons:
            topic = l.get("topic", "General")
            if topic != current_topic:
                if current_unit_lessons:
                    units.append({
                        "title": current_topic or "General",
                        "lessons": current_unit_lessons,
                        "endOfUnitAssessment": False,
                    })
                current_topic = topic
                current_unit_lessons = []

            current_unit_lessons.append({
                "number": l.get("lesson_number", 0),
                "title": l.get("title", ""),
                "objectives": [l.get("spec_content", "")] if l.get("spec_content") else [],
                "keyVocabulary": [v.strip() for v in (l.get("key_vocabulary") or "").split(",") if v.strip()],
                "resources": "",
                "assessment": None,
                "crossCurricular": [],
            })

        if current_unit_lessons:
            units.append({
                "title": current_topic or "General",
                "lessons": current_unit_lessons,
                "endOfUnitAssessment": False,
            })

        terms.append({
            "name": f"Year {year}",
            "units": units,
        })

    title = course_config.get("name", "Imported Scheme")
    subject = course_config.get("subjects", [""])[0] if course_config.get("subjects") else ""
    year_group = sorted(by_year.keys())[0] if by_year else 0

    # Check for existing scheme with same title+subject+yearGroup
    existing = find_existing_scheme(title, subject, year_group)

    scheme = {
        "id": existing["id"] if existing else str(uuid.uuid4())[:8],
        "subject": subject,
        "keyStage": f"KS{course_config.get('key_stage', '')}" if course_config.get("key_stage") else "",
        "yearGroup": year_group,
        "examBoard": course_config.get("exam_board", ""),
        "totalLessons": len(lessons),
        "title": title,
        "source": "imported",
        "terms": terms,
        "created_at": existing.get("created_at", datetime.utcnow().isoformat()) if existing else datetime.utcnow().isoformat(),
    }

    saved = save_scheme(scheme)
    if existing:
        logger.info(f"Updated existing scheme {existing['id']} instead of creating duplicate")
    return saved


def cleanup_duplicate_schemes():
    """One-time cleanup: find duplicate schemes (same title+subject+yearGroup)
    and keep only the latest, deleting the rest. Returns count of deleted."""
    groups = {}
    for p in sorted(SCHEMES_DIR.glob("*.json")):
        if p.stem.endswith("_review"):
            continue
        try:
            data = json.loads(p.read_text())
            key = (
                data.get("title", "").strip().lower(),
                data.get("subject", "").strip().lower(),
                str(data.get("yearGroup", data.get("year_group", ""))).strip(),
            )
            ts = data.get("updated_at") or data.get("created_at") or ""
            groups.setdefault(key, []).append((ts, p, data.get("id", p.stem)))
        except (json.JSONDecodeError, KeyError):
            continue

    deleted = 0
    for key, entries in groups.items():
        if len(entries) <= 1:
            continue
        # Sort by timestamp desc — keep the newest
        entries.sort(key=lambda x: x[0], reverse=True)
        for ts, p, sid in entries[1:]:
            logger.info(f"Deleting duplicate scheme {sid} ({p.name})")
            p.unlink(missing_ok=True)
            # Also remove its review if present
            review = _review_path(sid)
            if review.exists():
                review.unlink()
            deleted += 1
    return deleted


def import_from_file(file_path, subject=None, key_stage=None, year_group=None,
                     exam_board=None):
    """Import a scheme from an uploaded file (xlsx, docx, csv).
    Parses the file into the scheme JSON structure."""
    ext = Path(file_path).suffix.lower()

    lessons = []
    if ext in (".xlsx", ".xls"):
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        for ws in wb.worksheets:
            headers = [str(c.value or "").strip().lower() for c in ws[1]]
            for row in ws.iter_rows(min_row=2, values_only=True):
                row_dict = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                title = (row_dict.get("title") or row_dict.get("lesson title") or
                         row_dict.get("lesson") or "")
                if not title:
                    continue
                lessons.append({
                    "lesson_number": len(lessons) + 1,
                    "title": str(title),
                    "topic": str(row_dict.get("topic") or row_dict.get("unit") or "General"),
                    "spec_content": str(row_dict.get("spec content") or row_dict.get("objectives") or
                                       row_dict.get("content") or ""),
                    "key_vocabulary": str(row_dict.get("key vocabulary") or row_dict.get("vocabulary") or ""),
                    "year": int(year_group) if year_group else 0,
                })
    elif ext == ".csv":
        import csv
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_lc = {k.strip().lower(): v for k, v in row.items()}
                title = (row_lc.get("title") or row_lc.get("lesson title") or
                         row_lc.get("lesson") or "")
                if not title:
                    continue
                lessons.append({
                    "lesson_number": len(lessons) + 1,
                    "title": str(title),
                    "topic": str(row_lc.get("topic") or row_lc.get("unit") or "General"),
                    "spec_content": str(row_lc.get("spec content") or row_lc.get("objectives") or ""),
                    "key_vocabulary": str(row_lc.get("key vocabulary") or row_lc.get("vocabulary") or ""),
                    "year": int(year_group) if year_group else 0,
                })
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please upload .xlsx, .xls, or .csv")

    if not lessons:
        raise ValueError("No lessons found in uploaded file. Check column headers include 'Title' or 'Lesson'.")

    # Build terms/units structure
    units = []
    current_topic = None
    current_lessons = []
    for l in lessons:
        topic = l.get("topic", "General")
        if topic != current_topic:
            if current_lessons:
                units.append({"title": current_topic or "General",
                              "lessons": current_lessons,
                              "endOfUnitAssessment": False})
            current_topic = topic
            current_lessons = []
        current_lessons.append({
            "number": l["lesson_number"],
            "title": l["title"],
            "objectives": [l["spec_content"]] if l["spec_content"] else [],
            "keyVocabulary": [v.strip() for v in l["key_vocabulary"].split(",") if v.strip()],
            "resources": "",
            "assessment": None,
            "crossCurricular": [],
        })
    if current_lessons:
        units.append({"title": current_topic or "General",
                      "lessons": current_lessons,
                      "endOfUnitAssessment": False})

    title_str = f"{subject or 'Imported'} — Year {year_group or '?'} ({key_stage or ''})"

    # Check for existing duplicate
    existing = find_existing_scheme(title_str, subject, year_group)

    scheme = {
        "id": existing["id"] if existing else str(uuid.uuid4())[:8],
        "subject": subject or "",
        "keyStage": key_stage or "",
        "yearGroup": int(year_group) if year_group else 0,
        "examBoard": exam_board or "",
        "totalLessons": len(lessons),
        "title": title_str,
        "source": "file_upload",
        "terms": [{"name": f"Year {year_group or '?'}", "units": units}],
        "created_at": existing.get("created_at", datetime.utcnow().isoformat()) if existing else datetime.utcnow().isoformat(),
    }

    return save_scheme(scheme)


# ───────────────────────────────────────────────────────────────────
# AI Review
# ───────────────────────────────────────────────────────────────────

def review_scheme(scheme_id, reference_context="", model="claude-sonnet-4-5-20250929"):
    """
    Run an AI review of a scheme of work against reference documents.

    Returns structured review with strengths, improvements, missing content,
    and suggested resequencing.
    """
    scheme = get_scheme(scheme_id)
    if not scheme:
        raise ValueError(f"Scheme not found: {scheme_id}")

    start = time.time()

    user_prompt = f"""Review this scheme of work against the reference materials provided.

REFERENCE MATERIALS:
{reference_context if reference_context else "(No reference documents uploaded yet. Review based on general UK curriculum best practice.)"}

SCHEME OF WORK TO REVIEW:
{json.dumps(scheme, indent=2)}

REVIEW AGAINST THESE CRITERIA:
1. CURRICULUM COVERAGE — Does it cover all required content? Any gaps?
2. SEQUENCING & PROGRESSION — Is the lesson sequence logical? Does prior knowledge build?
3. EXPERT INPUT ALIGNMENT — Does it follow subject-specific pedagogical guidance?
4. QUALITY FRAMEWORK ALIGNMENT — Does it meet quality criteria?
5. BALANCE & BREADTH — Good mix of knowledge and skills? Assessment points?

Return your review as JSON with this EXACT structure:
{{
    "overallRating": "excellent" or "good" or "requires_improvement" or "inadequate",
    "overallSummary": "2-3 sentence summary",
    "strengths": [
        {{
            "area": "string",
            "detail": "specific praise",
            "evidence": "which part of the SoW demonstrates this"
        }}
    ],
    "improvements": [
        {{
            "area": "string",
            "issue": "what is wrong or missing",
            "suggestion": "specific actionable improvement",
            "priority": "critical" or "important" or "nice_to_have",
            "reference": "which reference document this comes from (or general best practice)",
            "affectedLessons": [1, 2, 3] or null
        }}
    ],
    "missingContent": [
        {{
            "topic": "string",
            "source": "National Curriculum / Specification / best practice",
            "suggestedPlacement": "After Unit X, Lesson Y",
            "estimatedLessons": 2
        }}
    ],
    "suggestedResequencing": [
        {{
            "current": "description of current placement",
            "suggested": "suggested new placement",
            "rationale": "why this change would improve the scheme"
        }}
    ]
}}"""

    messages = [{"role": "user", "content": user_prompt}]

    system_parts = [
        {
            "type": "text",
            "text": SOW_REVIEW_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    response = _create_message(
        model=model,
        max_tokens=8000,
        system=system_parts,
        messages=messages,
    )

    duration = round(time.time() - start, 1)
    raw_text = response.content[0].text.strip()

    try:
        review = _repair_json(raw_text, expect_object=True)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse review JSON: {e}\nRaw: {raw_text[:800]}")
        review = {
            "overallRating": "requires_improvement",
            "overallSummary": "Review generated but output could not be parsed as JSON.",
            "rawResponse": raw_text,
            "strengths": [],
            "improvements": [],
            "missingContent": [],
            "suggestedResequencing": [],
        }

    # Save review
    review["reviewed_at"] = datetime.utcnow().isoformat()
    review["model"] = model
    review["duration_s"] = duration
    review["usage"] = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    _review_path(scheme_id).write_text(json.dumps(review, indent=2))
    return review


# ───────────────────────────────────────────────────────────────────
# AI Generation
# ───────────────────────────────────────────────────────────────────

def generate_scheme(subject, key_stage, year_group, lessons_per_week=3,
                    weeks_per_term=6, exam_board=None, priorities=None,
                    exclusions=None, reference_context="",
                    model="claude-sonnet-4-5-20250929"):
    """
    Generate a complete scheme of work from scratch using AI.

    Returns saved scheme data.
    """
    start = time.time()

    total_terms = 6  # UK academic year: 6 half-terms
    total_lessons = lessons_per_week * weeks_per_term * total_terms
    term_names = ["Autumn 1", "Autumn 2", "Spring 1", "Spring 2", "Summer 1", "Summer 2"]

    user_prompt = f"""Generate a complete scheme of work for:
- Subject: {subject}
- Key Stage: {key_stage}
- Year Group: {year_group}
- Exam Board: {exam_board or "N/A"}
- Lessons per week: {lessons_per_week}
- Weeks per term (half-term): {weeks_per_term}
- Total lessons: {total_lessons}
- Terms: {', '.join(term_names)}

{f"PRIORITISE THESE TOPICS: {priorities}" if priorities else ""}
{f"EXCLUDE THESE TOPICS: {exclusions}" if exclusions else ""}

REFERENCE MATERIALS:
{reference_context if reference_context else "(No reference documents uploaded. Generate based on UK National Curriculum / specification best practice.)"}

Return the scheme as JSON with this EXACT structure:
{{
    "subject": "{subject}",
    "keyStage": "{key_stage}",
    "yearGroup": {year_group},
    "examBoard": {json.dumps(exam_board)},
    "totalLessons": {total_lessons},
    "terms": [
        {{
            "name": "Autumn 1",
            "units": [
                {{
                    "title": "Unit title",
                    "lessons": [
                        {{
                            "number": 1,
                            "title": "Lesson title",
                            "objectives": ["Students will be able to..."],
                            "keyVocabulary": ["term1", "term2"],
                            "resources": "Required resources",
                            "assessment": null or "End of unit test",
                            "crossCurricular": ["Maths - measurement"]
                        }}
                    ],
                    "endOfUnitAssessment": true or false
                }}
            ]
        }}
    ]
}}

Ensure EVERY lesson has a number, title, objectives, and key vocabulary.
Number lessons sequentially across the whole year (1 to {total_lessons})."""

    system_parts = [
        {
            "type": "text",
            "text": SOW_GENERATE_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    response = _create_message(
        model=model,
        max_tokens=32000,
        system=system_parts,
        messages=[{"role": "user", "content": user_prompt}],
    )

    duration = round(time.time() - start, 1)
    raw_text = response.content[0].text.strip()
    stop_reason = response.stop_reason

    if stop_reason == "max_tokens":
        logger.warning(f"Scheme generation hit max_tokens — output likely truncated ({len(raw_text)} chars)")

    try:
        scheme_data = _repair_json(raw_text, expect_object=True)
        if stop_reason == "max_tokens":
            logger.info("Successfully repaired truncated JSON from scheme generation")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse generated SoW JSON: {e}\nRaw: {raw_text[:800]}")
        raise ValueError(f"AI generated invalid JSON for scheme: {e}")

    # Add metadata
    scheme_data["id"] = str(uuid.uuid4())[:8]
    scheme_data["source"] = "ai_generated"
    scheme_data["title"] = f"{subject} — Year {year_group} ({key_stage})"
    scheme_data["generation"] = {
        "model": model,
        "duration_s": duration,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }

    return save_scheme(scheme_data)


# ───────────────────────────────────────────────────────────────────
# Apply suggestion
# ───────────────────────────────────────────────────────────────────

def apply_suggestion(scheme_id, suggestion, reference_context="",
                     model="claude-sonnet-4-5-20250929"):
    """Apply a single review suggestion to a scheme, returning updated scheme."""
    scheme = get_scheme(scheme_id)
    if not scheme:
        raise ValueError(f"Scheme not found: {scheme_id}")

    start = time.time()

    user_prompt = f"""Apply this suggestion to the scheme of work:

SUGGESTION:
{json.dumps(suggestion, indent=2)}

CURRENT SCHEME:
{json.dumps(scheme, indent=2)}

Return the COMPLETE modified scheme as JSON (same structure, with the suggestion applied).
Do NOT remove or change anything else — only apply the requested change."""

    response = _create_message(
        model=model,
        max_tokens=16000,
        system=[{
            "type": "text",
            "text": SOW_APPLY_SUGGESTION_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_prompt}],
    )

    duration = round(time.time() - start, 1)
    raw_text = response.content[0].text.strip()

    try:
        updated = _repair_json(raw_text, expect_object=True)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON for updated scheme: {e}")

    # Preserve metadata
    updated["id"] = scheme["id"]
    updated["created_at"] = scheme.get("created_at", "")
    updated["source"] = scheme.get("source", "")
    return save_scheme(updated)


# ───────────────────────────────────────────────────────────────────
# Export to pipeline-compatible Excel
# ───────────────────────────────────────────────────────────────────

def export_to_excel(scheme_id, output_path=None):
    """Export a scheme to Excel in the format the pipeline expects."""
    scheme = get_scheme(scheme_id)
    if not scheme:
        raise ValueError(f"Scheme not found: {scheme_id}")

    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Year {scheme.get('yearGroup', '')} Lessons"

    # Headers matching the pipeline col_map
    headers = ["Week", "Lesson #", "Subject", "Topic", "Title",
               "Spec Content", "RP", "Key Vocabulary", "WS/MS", "HT Only"]
    ws.append(headers)

    lesson_num = 0
    for term in scheme.get("terms", []):
        for unit in term.get("units", []):
            for lesson in unit.get("lessons", []):
                lesson_num += 1
                ws.append([
                    "",  # Week
                    lesson.get("number", lesson_num),
                    scheme.get("subject", ""),
                    unit.get("title", ""),
                    lesson.get("title", ""),
                    "; ".join(lesson.get("objectives", [])),
                    "",  # Required Practical
                    ", ".join(lesson.get("keyVocabulary", [])),
                    "",  # WS/MS
                    "",  # HT Only
                ])

    if not output_path:
        output_dir = Path(__file__).parent / "output" / "schemes"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_title = re.sub(r"[^\w\s-]", "", scheme.get("title", "scheme")).replace(" ", "_")
        output_path = str(output_dir / f"{safe_title}.xlsx")

    wb.save(output_path)
    return output_path
