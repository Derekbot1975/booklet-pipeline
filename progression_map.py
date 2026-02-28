"""
Curriculum Progression Map Builder (Prompt Sheet 14).

Generates visual, child-centred progression maps showing:
  - Every unit/topic as a node
  - Connections between topics
  - Prior and future learning links
  - Timeline across the year
  - Strand colour-coding

Outputs:
  - Interactive SVG data for web display
  - PDF poster (via HTML template)
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
    # Remove trailing commas before } or ]
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw


def _repair_json(raw):
    """Attempt to repair truncated JSON by closing open brackets/braces.

    Handles common AI truncation: mid-string cuts, missing closing
    brackets, trailing commas, and partial key-value pairs.
    """
    # First try as-is
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Step 1: Find the last complete key-value pair or structural element.
    # Walk backwards from the end, looking for the last complete JSON value
    # (ends with ", number, true, false, null, }, or ]).
    # We progressively chop the tail and try to close brackets.

    # Quick attempt: strip everything after the last complete } or ] or "
    for trim_pattern in [
        # Remove incomplete trailing string value and its key
        r',\s*"[^"]*"\s*:\s*"[^"]*$',
        # Remove trailing incomplete string
        r'"[^"]*$',
        # Remove trailing partial number/bool
        r',\s*"[^"]*"\s*:\s*\S*$',
        # Remove trailing comma and whitespace
        r',\s*$',
    ]:
        candidate = re.sub(trim_pattern, '', raw)
        if candidate != raw:
            result = _try_close_json(candidate)
            if result is not None:
                return result

    # Step 2: Brute force — progressively trim from the end
    for cut_pos in range(len(raw) - 1, max(0, len(raw) - 500), -1):
        ch = raw[cut_pos]
        if ch in '"}]0123456789':
            candidate = raw[:cut_pos + 1]
            result = _try_close_json(candidate)
            if result is not None:
                return result

    raise json.JSONDecodeError("Could not repair truncated JSON", raw, 0)


def _try_close_json(fragment):
    """Try to close open brackets/braces in a JSON fragment and parse it."""
    # Remove trailing commas
    fragment = re.sub(r",\s*$", "", fragment.rstrip())
    fragment = re.sub(r",\s*([}\]])", r"\1", fragment)

    # Count open structures (ignoring string contents)
    in_string = False
    escape = False
    stack = []
    for ch in fragment:
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            stack.append('}')
        elif ch == '[':
            stack.append(']')
        elif ch in '}]' and stack and stack[-1] == ch:
            stack.pop()

    # If we're still inside a string, close it
    if in_string:
        fragment += '"'

    # Close all open structures
    closers = "".join(reversed(stack))
    candidate = fragment + closers
    candidate = re.sub(r",\s*([}\]])", r"\1", candidate)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


MAPS_DIR = Path(__file__).parent / "data" / "progression-maps"
MAPS_DIR.mkdir(parents=True, exist_ok=True)


MAP_GENERATION_PROMPT = """You are a curriculum design expert creating a student-facing progression map.
This must be visually engaging and show the learning journey.

LANGUAGE: Use UK English throughout.
TONE: Student-friendly — "You will learn..." not "Students will be taught..."

OUTPUT: Return valid JSON matching the schema below. Do NOT wrap in code fences.

The map should be MOTIVATIONAL:
- Show students WHERE they are going and WHY
- Use engaging language and big questions
- Make each unit sound exciting and purposeful
- Show how topics connect to each other and to real life"""


def _get_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_progression_map(scheme, reference_context="",
                             model="claude-sonnet-4-5-20250929"):
    """
    Generate a progression map from a scheme of work.

    Returns saved map data with nodes, connections, and metadata.
    """
    client = _get_client()
    start = time.time()

    user_prompt = f"""Generate a curriculum progression map for this scheme of work.

SCHEME:
{json.dumps(scheme, indent=2)}

{f"REFERENCE MATERIALS:{chr(10)}{reference_context}" if reference_context else ""}

Return JSON with this structure:
{{
    "title": "Your Year {scheme.get('yearGroup', '?')} {scheme.get('subject', '')} Journey",
    "subtitle": "Everything you will discover this year",
    "yearGroup": {scheme.get('yearGroup', 0)},
    "subject": "{scheme.get('subject', '')}",
    "strands": [
        {{
            "name": "Strand name (e.g. Biology, Forces, Modern History)",
            "colour": "#hex colour",
            "icon": "emoji icon"
        }}
    ],
    "nodes": [
        {{
            "id": "unit-1",
            "title": "Unit title",
            "studentDescription": "You will discover... (1 short sentence)",
            "strand": "Strand name",
            "term": "Autumn 1",
            "position": 1,
            "keyVocabulary": ["term1", "term2", "term3"],
            "bigQuestion": "An intriguing question this unit answers",
            "lessonCount": 6,
            "assessmentPoint": true or false
        }}
    ],
    "connections": [
        {{
            "from": "unit-1",
            "to": "unit-3",
            "type": "builds_on" or "links_to" or "contrasts_with",
            "label": "Short description of the connection"
        }}
    ],
    "priorLearning": [
        {{
            "yearGroup": {scheme.get('yearGroup', 0) - 1},
            "topic": "What students learned before",
            "linksTo": "unit-1"
        }}
    ],
    "futureLearning": [
        {{
            "yearGroup": {scheme.get('yearGroup', 0) + 1},
            "topic": "What students will learn next",
            "linksFrom": "unit-X"
        }}
    ]
}}

RULES:
- Every unit in the scheme must appear as a node
- Include at least 3-5 meaningful connections between units
- Student descriptions must be written for the age group (Year {scheme.get('yearGroup', '?')})
- Big questions should be genuinely intriguing
- Strand colours should be distinct and visually appealing
- Include prior and future learning links where relevant"""

    response = client.messages.create(
        model=model,
        max_tokens=16000,
        system=[{
            "type": "text",
            "text": MAP_GENERATION_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_prompt}],
    )

    duration = round(time.time() - start, 1)
    raw = response.content[0].text.strip()

    raw = _extract_json(raw, expect_object=True)

    try:
        map_data = json.loads(raw)
    except json.JSONDecodeError:
        # Response may have been truncated — attempt repair
        logger.warning("Direct JSON parse failed, attempting repair...")
        try:
            map_data = _repair_json(raw)
            logger.info("JSON repair succeeded")
        except json.JSONDecodeError as e2:
            logger.error(f"Failed to parse/repair map JSON: {e2}\nRaw: {raw[:800]}")
            raise ValueError(f"AI generated invalid JSON for progression map: {e2}")

    # Add metadata
    map_data["id"] = str(uuid.uuid4())[:8]
    map_data["scheme_id"] = scheme.get("id", "")
    map_data["created_at"] = datetime.utcnow().isoformat()
    map_data["generation"] = {
        "model": model,
        "duration_s": duration,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }

    # Save JSON data
    path = MAPS_DIR / f"{map_data['id']}.json"
    path.write_text(json.dumps(map_data, indent=2))

    # Auto-export SVG + PDF to output folder
    try:
        exported = export_to_files(map_data, scheme)
        map_data["exported_files"] = exported
        # Re-save with export paths
        path.write_text(json.dumps(map_data, indent=2))
    except Exception as e:
        logger.warning(f"Auto-export failed (map still saved): {e}")

    return map_data


# ───────────────────────────────────────────────────────────────────
# File export (SVG + PDF)
# ───────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent / "output"


def export_to_files(map_data, scheme=None):
    """
    Export a progression map as SVG and PDF to the output folder.

    Saves to: output/{course_name}/Progression Maps/{title}.svg (and .pdf)
    Returns dict with file paths.
    """
    import subprocess

    subject = map_data.get("subject", "Unknown")
    year = map_data.get("yearGroup", "")
    title = map_data.get("title", f"Year {year} {subject} Journey")
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()

    # Build output folder — match existing pattern
    course_name = "Progression Maps"
    if scheme:
        course_name = scheme.get("title", "") or scheme.get("subject", "")
        course_name = re.sub(r'[<>:"/\\|?*]', '', course_name).strip() or "Progression Maps"

    out_dir = OUTPUT_DIR / course_name / "Progression Maps"
    out_dir.mkdir(parents=True, exist_ok=True)

    exported = {}

    # 1. Save SVG
    svg_content = render_svg(map_data)
    svg_path = out_dir / f"{safe_title}.svg"
    svg_path.write_text(svg_content, encoding="utf-8")
    exported["svg"] = str(svg_path)
    logger.info(f"Saved SVG: {svg_path}")

    # 2. Convert SVG → PDF via a lightweight HTML wrapper + wkhtmltopdf or LibreOffice
    #    Fallback: wrap SVG in HTML and use LibreOffice or just keep SVG
    pdf_path = out_dir / f"{safe_title}.pdf"
    try:
        # Try using LibreOffice to convert SVG to PDF (commonly available)
        result = subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", str(out_dir), str(svg_path)],
            capture_output=True, text=True, timeout=30,
        )
        if pdf_path.exists():
            exported["pdf"] = str(pdf_path)
            logger.info(f"Saved PDF: {pdf_path}")
        else:
            # LibreOffice might have worked but with different filename
            logger.warning(f"PDF conversion ran but file not found at {pdf_path}")
    except FileNotFoundError:
        logger.info("LibreOffice not available for PDF conversion — SVG only")
    except subprocess.TimeoutExpired:
        logger.warning("PDF conversion timed out — SVG only")
    except Exception as e:
        logger.warning(f"PDF conversion failed: {e} — SVG only")

    return exported


# ───────────────────────────────────────────────────────────────────
# CRUD
# ───────────────────────────────────────────────────────────────────

def list_maps(subject=None):
    """List all progression maps."""
    maps = []
    for p in sorted(MAPS_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            if subject and data.get("subject", "").lower() != subject.lower():
                continue
            maps.append({
                "id": data["id"],
                "title": data.get("title", ""),
                "subject": data.get("subject", ""),
                "yearGroup": data.get("yearGroup", ""),
                "scheme_id": data.get("scheme_id", ""),
                "node_count": len(data.get("nodes", [])),
                "connection_count": len(data.get("connections", [])),
                "created_at": data.get("created_at", ""),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return maps


def get_map(map_id):
    """Get a full progression map by ID."""
    path = MAPS_DIR / f"{map_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def update_map(map_id, updates):
    """Update a progression map."""
    path = MAPS_DIR / f"{map_id}.json"
    if not path.exists():
        raise ValueError(f"Map not found: {map_id}")
    data = json.loads(path.read_text())
    data.update(updates)
    data["updated_at"] = datetime.utcnow().isoformat()
    path.write_text(json.dumps(data, indent=2))
    return data


def delete_map(map_id):
    """Delete a progression map."""
    path = MAPS_DIR / f"{map_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


# ───────────────────────────────────────────────────────────────────
# SVG rendering — road-style learning journey
# ───────────────────────────────────────────────────────────────────

def _road_waypoints(n_nodes, width, start_y, row_height, margin_x):
    """
    Generate a list of (x, y) waypoints that trace an S-shaped road.
    Nodes are placed along the road from bottom to top, snaking
    left→right then right→left each row.
    """
    pts = []
    cols_per_row = 3  # nodes per horizontal run
    rows_needed = (n_nodes + cols_per_row - 1) // cols_per_row
    left_x = margin_x
    right_x = width - margin_x

    idx = 0
    for row in range(rows_needed):
        y = start_y - row * row_height
        going_right = (row % 2 == 0)
        cols_this_row = min(cols_per_row, n_nodes - idx)
        for col in range(cols_this_row):
            if going_right:
                frac = col / max(cols_this_row - 1, 1)
                x = left_x + frac * (right_x - left_x)
            else:
                frac = col / max(cols_this_row - 1, 1)
                x = right_x - frac * (right_x - left_x)
            pts.append((x, y))
            idx += 1
    return pts


def _build_road_path(waypoints, road_w):
    """Return SVG <path> d-strings for the road's outer edge, centre dash, and kerb."""
    if len(waypoints) < 2:
        return "", ""

    # Build a smooth cubic-bezier path through all waypoints
    d_parts = [f"M {waypoints[0][0]},{waypoints[0][1]}"]
    for i in range(1, len(waypoints)):
        x0, y0 = waypoints[i - 1]
        x1, y1 = waypoints[i]
        # Use vertical control points for smooth S-curves
        cy = (y0 + y1) / 2
        d_parts.append(f"C {x0},{cy} {x1},{cy} {x1},{y1}")

    path_d = " ".join(d_parts)
    return path_d, path_d  # same path for road and centre line


def render_svg(map_data):
    """
    Render a progression map as a road-style learning journey SVG.
    Inspired by school learning journey maps with a winding road,
    year-group circles, topic milestones, and a dark background.
    """
    nodes = map_data.get("nodes", [])
    strands = {s["name"]: s for s in map_data.get("strands", [])}
    title = map_data.get("title", "Learning Journey")
    subtitle = map_data.get("subtitle", "")
    subject = map_data.get("subject", "")
    year_group = map_data.get("yearGroup", "")

    # Sort nodes by term order then position
    term_order = {
        "Autumn 1": 0, "Autumn 2": 1,
        "Spring 1": 2, "Spring 2": 3,
        "Summer 1": 4, "Summer 2": 5,
    }
    sorted_nodes = sorted(nodes, key=lambda n: (
        term_order.get(n.get("term", "Autumn 1"), 0),
        n.get("position", 0),
    ))

    n = len(sorted_nodes) or 1
    # Dimensions — landscape poster
    width = 1400
    margin_x = 200
    row_height = 200
    cols_per_row = 3
    rows = (n + cols_per_row - 1) // cols_per_row
    height = max(700, 180 + rows * row_height + 80)
    road_start_y = height - 100

    # Generate waypoints for nodes
    waypoints = _road_waypoints(n, width, road_start_y, row_height, margin_x)

    # Build road path
    road_d, centre_d = _build_road_path(waypoints, 60)

    # --- Start SVG ---
    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'style="font-family: \'Segoe UI\', -apple-system, sans-serif;">'
    )

    # Defs — filters and gradients
    svg.append('''<defs>
  <filter id="shadow" x="-10%" y="-10%" width="130%" height="130%">
    <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.3"/>
  </filter>
  <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#1a1a2e"/>
    <stop offset="100%" stop-color="#16213e"/>
  </linearGradient>
  <linearGradient id="bannerGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#2d6a30"/>
    <stop offset="100%" stop-color="#4a9e4e"/>
  </linearGradient>
</defs>''')

    # Background
    svg.append(f'<rect width="{width}" height="{height}" fill="url(#bgGrad)"/>')

    # Subtle stars on background
    import random
    rng = random.Random(42)  # deterministic
    for _ in range(60):
        sx, sy = rng.randint(0, width), rng.randint(0, height)
        sr = rng.uniform(0.5, 1.5)
        so = rng.uniform(0.3, 0.8)
        svg.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#fff" opacity="{so:.1f}"/>')

    # ── Title banner ──
    bw = min(width - 40, 1000)
    bx = (width - bw) / 2
    svg.append(f'<rect x="{bx}" y="18" width="{bw}" height="52" rx="4" fill="url(#bannerGrad)"/>')
    svg.append(f'<rect x="{bx}" y="18" width="6" height="52" fill="#e8b230"/>') # gold accent
    svg.append(
        f'<text x="{bx + 30}" y="52" font-size="26" font-weight="800" fill="#fff" '
        f'letter-spacing="2">LEARNING JOURNEY</text>'
    )
    if subject or year_group:
        label = f"Year {year_group} {subject}" if year_group else subject
        svg.append(
            f'<text x="{bx + bw - 20}" y="52" text-anchor="end" font-size="16" '
            f'font-weight="600" fill="#e8e8e8">{_esc(label)}</text>'
        )

    # Subtitle
    if subtitle:
        svg.append(
            f'<text x="{width/2}" y="90" text-anchor="middle" font-size="13" '
            f'fill="#c8c8d0" font-style="italic">{_esc(subtitle)}</text>'
        )

    # ── Road ──
    if road_d:
        # Road surface (dark grey)
        svg.append(
            f'<path d="{road_d}" fill="none" stroke="#3a3a3a" '
            f'stroke-width="64" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        # Road edges (yellow kerb lines)
        svg.append(
            f'<path d="{road_d}" fill="none" stroke="#e8b230" '
            f'stroke-width="68" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>'
        )
        # Actual road on top
        svg.append(
            f'<path d="{road_d}" fill="none" stroke="#3a3a3a" '
            f'stroke-width="60" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        # Centre dashed line
        svg.append(
            f'<path d="{centre_d}" fill="none" stroke="#e8e8e8" '
            f'stroke-width="2" stroke-dasharray="12,10" stroke-linecap="round"/>'
        )

    # ── Term dividers — dashed lines across road at term boundaries ──
    current_term = None
    for i, node in enumerate(sorted_nodes):
        term = node.get("term", "Autumn 1")
        if term != current_term and i > 0 and i < len(waypoints):
            # Draw a dashed separator between terms
            wx, wy = waypoints[i]
            svg.append(
                f'<line x1="{wx - 90}" y1="{wy}" x2="{wx + 90}" y2="{wy}" '
                f'stroke="#e8b230" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.4"/>'
            )
        current_term = term

    # ── Nodes as milestones along the road ──
    prev_term = None
    term_label_placed = set()

    for i, node in enumerate(sorted_nodes):
        if i >= len(waypoints):
            break
        cx, cy = waypoints[i]
        strand_info = strands.get(node.get("strand", ""), {})
        colour = strand_info.get("colour", "#4a9e4e")
        icon = strand_info.get("icon", "📚")
        term = node.get("term", "Autumn 1")
        node_title = node.get("title", "")[:28]
        bq = node.get("bigQuestion", "")[:50]
        is_assessment = node.get("assessmentPoint", False)

        # --- Term label (at first node in each new term) ---
        if term not in term_label_placed:
            term_label_placed.add(term)
            # Place term label as a banner near the road
            tlx = cx
            tly = cy + 45
            svg.append(
                f'<rect x="{tlx - 50}" y="{tly - 10}" width="100" height="20" rx="10" '
                f'fill="#e8b230" opacity="0.9"/>'
            )
            svg.append(
                f'<text x="{tlx}" y="{tly + 5}" text-anchor="middle" font-size="10" '
                f'font-weight="700" fill="#1a1a2e">{_esc(term)}</text>'
            )

        # --- Node circle (milestone on road) ---
        r = 28 if is_assessment else 22
        # Glow
        svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="{colour}" opacity="0.2"/>'
        )
        # Outer ring
        svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2a2a3e" '
            f'stroke="{colour}" stroke-width="4"/>'
        )
        # Icon in circle
        svg.append(
            f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="16">'
            f'{icon}</text>'
        )

        # Assessment badge
        if is_assessment:
            svg.append(
                f'<circle cx="{cx + r - 2}" cy="{cy - r + 2}" r="8" fill="#e63946"/>'
            )
            svg.append(
                f'<text x="{cx + r - 2}" y="{cy - r + 6}" text-anchor="middle" '
                f'font-size="8" font-weight="bold" fill="#fff">T</text>'
            )

        # --- Topic label (beside the node) ---
        # Alternate labels left/right based on position
        label_side = 1 if (i % 2 == 0) else -1
        lx = cx + label_side * (r + 15)
        anchor = "start" if label_side > 0 else "end"

        # Title
        svg.append(
            f'<text x="{lx}" y="{cy - 8}" text-anchor="{anchor}" '
            f'font-size="11" font-weight="700" fill="#fff">{_esc(node_title)}</text>'
        )
        # Big question
        if bq:
            svg.append(
                f'<text x="{lx}" y="{cy + 6}" text-anchor="{anchor}" '
                f'font-size="9" fill="#b8b8c8" font-style="italic">{_esc(bq)}</text>'
            )
        # Key vocab (small)
        vocab = node.get("keyVocabulary", [])[:3]
        if vocab:
            vocab_str = " · ".join(vocab)
            svg.append(
                f'<text x="{lx}" y="{cy + 19}" text-anchor="{anchor}" '
                f'font-size="8" fill="#7a7a8c">{_esc(vocab_str)}</text>'
            )

    # ── Strand legend ──
    strand_list = map_data.get("strands", [])
    if strand_list:
        lx = 30
        ly = height - 20 - len(strand_list) * 22
        svg.append(
            f'<rect x="{lx - 10}" y="{ly - 16}" width="180" '
            f'height="{len(strand_list) * 22 + 20}" rx="8" fill="#0d0d1a" opacity="0.7"/>'
        )
        for si, strand in enumerate(strand_list):
            sy = ly + si * 22
            sc = strand.get("colour", "#4a9e4e")
            sicon = strand.get("icon", "")
            sname = strand.get("name", "")
            svg.append(f'<circle cx="{lx + 6}" cy="{sy}" r="6" fill="{sc}"/>')
            svg.append(
                f'<text x="{lx + 18}" y="{sy + 4}" font-size="10" fill="#d0d0d8">'
                f'{_esc(sicon)} {_esc(sname)}</text>'
            )

    # ── Prior / future learning ──
    prior = map_data.get("priorLearning", [])
    future = map_data.get("futureLearning", [])

    if prior:
        # Bottom-right corner
        px, py = width - 30, height - 15 - len(prior) * 16
        svg.append(
            f'<rect x="{px - 200}" y="{py - 18}" width="210" '
            f'height="{len(prior) * 16 + 26}" rx="8" fill="#0d0d1a" opacity="0.7"/>'
        )
        svg.append(
            f'<text x="{px - 190}" y="{py - 2}" font-size="9" font-weight="700" '
            f'fill="#e8b230">PRIOR LEARNING</text>'
        )
        for pi, p in enumerate(prior):
            svg.append(
                f'<text x="{px - 190}" y="{py + 14 + pi * 16}" font-size="9" '
                f'fill="#a0a0b0">Y{p.get("yearGroup", "?")} — {_esc(p.get("topic", "")[:35])}</text>'
            )

    if future:
        # Top-right corner
        fx, fy = width - 30, 100
        svg.append(
            f'<rect x="{fx - 200}" y="{fy - 2}" width="210" '
            f'height="{len(future) * 16 + 26}" rx="8" fill="#0d0d1a" opacity="0.7"/>'
        )
        svg.append(
            f'<text x="{fx - 190}" y="{fy + 14}" font-size="9" font-weight="700" '
            f'fill="#4a9e4e">FUTURE LEARNING</text>'
        )
        for fi, f_item in enumerate(future):
            svg.append(
                f'<text x="{fx - 190}" y="{fy + 30 + fi * 16}" font-size="9" '
                f'fill="#a0a0b0">Y{f_item.get("yearGroup", "?")} — '
                f'{_esc(f_item.get("topic", "")[:35])}</text>'
            )

    # ── Start / finish markers ──
    if waypoints:
        # Start flag (bottom)
        sx, sy = waypoints[0]
        svg.append(
            f'<text x="{sx}" y="{sy + 50}" text-anchor="middle" '
            f'font-size="20">🏁</text>'
        )
        svg.append(
            f'<text x="{sx}" y="{sy + 68}" text-anchor="middle" '
            f'font-size="10" font-weight="700" fill="#e8b230">START HERE</text>'
        )
        # Finish (top)
        ex, ey = waypoints[-1]
        svg.append(
            f'<text x="{ex}" y="{ey - 42}" text-anchor="middle" '
            f'font-size="20">🎓</text>'
        )
        svg.append(
            f'<text x="{ex}" y="{ey - 26}" text-anchor="middle" '
            f'font-size="10" font-weight="700" fill="#4a9e4e">WELL DONE!</text>'
        )

    svg.append('</svg>')
    return "\n".join(svg)


def _esc(text):
    """Escape text for SVG."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
