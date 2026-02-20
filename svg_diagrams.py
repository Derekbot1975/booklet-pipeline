"""
SVG diagram generation using Claude API.

Replaces DALL-E with Claude-generated SVG code for educational diagrams.
Produces scientifically accurate, clean line diagrams with proper labels,
correct circuit symbols, and consistent styling across all booklets.

Pipeline: Claude generates SVG code → cairosvg converts to PNG → embedded in docx.
"""

import hashlib
import logging
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

MAX_DIAGRAMS_PER_BOOKLET = 5  # cost control

SVG_SYSTEM_PROMPT = """You are a specialist at creating clean, accurate SVG diagrams for UK GCSE science textbooks.

RULES — you MUST follow ALL of these:

1. OUTPUT: Return ONLY valid SVG code. No explanation, no markdown, no code fences.
   Start with <svg and end with </svg>.

2. CANVAS: Use viewBox="0 0 800 600" (landscape) or viewBox="0 0 600 800" (portrait).
   Choose whichever orientation suits the subject best.

3. STYLE:
   - Black outlines on white background ONLY
   - Stroke width: 2px for main outlines, 1px for internal detail
   - Fill: white (#ffffff) for all enclosed regions — NO grey, NO colour
   - Font: Arial or sans-serif, 13px for labels, 11px for secondary text
   - All text must be horizontal and readable

4. LABELS:
   - Add clear text labels with leader lines (thin black lines from label to part)
   - Labels should be outside the diagram where possible
   - Use proper scientific terminology appropriate for GCSE level

5. ACCURACY:
   - Diagrams MUST be scientifically accurate
   - Circuit diagrams: use correct BSI circuit symbols (cell = two parallel lines
     long/short, resistor = rectangle, lamp = circle with X, ammeter = circle with A,
     voltmeter = circle with V, switch = break in line with dot)
   - Biology: correct proportions and structures
   - Chemistry: correct molecular representations
   - Physics: correct force arrows, ray diagrams, etc.

6. SIMPLICITY:
   - Maximum 6-8 labelled parts per diagram
   - Clean, uncluttered layout with generous spacing
   - No decorative elements, no borders, no backgrounds
   - Think: what would appear on a GCSE exam paper

7. ARROWS: Use proper arrowheads defined in <defs><marker>. Direction arrows should
   be clear and distinct from leader lines.

8. NO external images, NO embedded raster data, NO href links."""


def get_claude_client():
    """Get an Anthropic client for SVG generation."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        logger.warning(f"Could not create Anthropic client for diagrams: {e}")
        return None


def generate_svg_diagram(description, output_path):
    """
    Generate an educational diagram as SVG using Claude, then convert to PNG.

    Args:
        description: what the diagram should show
        output_path: where to save the PNG file

    Returns:
        str path to saved PNG, or None on failure
    """
    client = get_claude_client()
    if not client:
        logger.info("No Anthropic API key — skipping SVG diagram generation")
        return None

    prompt = (
        f"Create an SVG diagram of: {description}\n\n"
        "This is for a UK GCSE science self-study booklet. "
        "The diagram will be printed in black and white at approximately "
        "4 inches wide in a Word document. Make it clear and simple."
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            system=[{
                "type": "text",
                "text": SVG_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract SVG from response
        svg_content = ""
        for block in message.content:
            if block.type == "text":
                svg_content += block.text

        # Clean up — extract just the SVG if wrapped in anything
        svg_content = _extract_svg(svg_content)

        if not svg_content:
            logger.warning(f"Claude returned no valid SVG for: {description}")
            return None

        # Save SVG
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path = output_path.with_suffix(".svg")
        svg_path.write_text(svg_content)

        # Convert SVG → PNG
        png_path = _svg_to_png(svg_path, output_path)

        if png_path:
            logger.info(f"SVG diagram generated: {png_path}")
            return str(png_path)
        else:
            logger.warning(f"SVG to PNG conversion failed for: {description}")
            return None

    except Exception as e:
        logger.warning(f"SVG diagram generation failed for '{description}': {e}")
        return None


def _extract_svg(text):
    """Extract clean SVG content from Claude's response."""
    # Remove markdown code fences if present
    text = re.sub(r"```(?:svg|xml)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()

    # Find the SVG element
    match = re.search(r"(<svg[\s\S]*?</svg>)", text, re.IGNORECASE)
    if match:
        return match.group(1)

    # If the whole thing looks like SVG
    if text.startswith("<svg") and text.endswith("</svg>"):
        return text

    return None


def _svg_to_png(svg_path, png_path, width=1200):
    """
    Convert SVG to PNG using cairosvg.

    Args:
        svg_path: path to SVG file
        png_path: desired PNG output path
        width: output width in pixels (height auto-calculated)

    Returns:
        str path to PNG or None on failure
    """
    svg_path = Path(svg_path)
    png_path = Path(png_path).with_suffix(".png")

    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=width,
        )
        if png_path.exists() and png_path.stat().st_size > 0:
            return str(png_path)
    except Exception as e:
        logger.warning(f"cairosvg conversion failed: {e}")

    # Fallback: try LibreOffice
    try:
        import shutil
        import subprocess
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "png",
                 "--outdir", str(png_path.parent), str(svg_path)],
                capture_output=True, timeout=30,
            )
            lo_output = svg_path.with_suffix(".png")
            if lo_output.exists():
                if lo_output != png_path:
                    lo_output.rename(png_path)
                return str(png_path)
    except Exception as e:
        logger.warning(f"LibreOffice SVG conversion failed: {e}")

    return None


def generate_diagrams_for_booklet(md_content, output_dir):
    """
    Scan markdown for [DRAWING SPACE: description] markers and generate
    SVG diagrams for each one using Claude.

    Args:
        md_content: the markdown text
        output_dir: directory to save diagram images

    Returns:
        dict mapping description strings to image file paths
    """
    client = get_claude_client()
    if not client:
        logger.info("No Anthropic API key — skipping diagram generation")
        return {}

    # Find all drawing space markers with descriptions
    pattern = r"\[DRAWING\s+SPACE:\s*(.+?)\]"
    matches = re.findall(pattern, md_content, re.IGNORECASE)

    if not matches:
        return {}

    # Deduplicate while preserving order
    seen = set()
    unique_descriptions = []
    for desc in matches:
        desc_lower = desc.strip().lower()
        if desc_lower not in seen:
            seen.add(desc_lower)
            unique_descriptions.append(desc.strip())

    # Limit to MAX_DIAGRAMS_PER_BOOKLET
    if len(unique_descriptions) > MAX_DIAGRAMS_PER_BOOKLET:
        logger.warning(
            f"Found {len(unique_descriptions)} diagram requests, "
            f"limiting to {MAX_DIAGRAMS_PER_BOOKLET}"
        )
        unique_descriptions = unique_descriptions[:MAX_DIAGRAMS_PER_BOOKLET]

    output_dir = Path(output_dir)
    diagrams_dir = output_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    result = {}

    for idx, desc in enumerate(unique_descriptions):
        # Create a stable filename from the description
        desc_hash = hashlib.md5(desc.lower().encode()).hexdigest()[:8]
        img_filename = f"diagram_{idx + 1}_{desc_hash}.png"
        img_path = diagrams_dir / img_filename

        # Skip if image already exists (caching)
        if img_path.exists():
            logger.info(f"Using cached diagram: {img_path}")
            result[desc] = str(img_path)
            continue

        # Generate
        logger.info(
            f"Generating SVG diagram {idx + 1}/{len(unique_descriptions)}: {desc}"
        )
        path = generate_svg_diagram(desc, str(img_path))

        if path:
            result[desc] = path

        # Small delay between API calls
        if idx < len(unique_descriptions) - 1:
            time.sleep(0.5)

    logger.info(f"Generated {len(result)}/{len(unique_descriptions)} diagrams")
    return result
