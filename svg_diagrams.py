"""
SVG diagram generation using Claude API.

Replaces DALL-E with Claude-generated SVG code for educational diagrams.
Produces clean, minimal technical line drawings with no text or labels —
students add their own labels by hand.

Pipeline: Claude generates SVG code → cairosvg/LibreOffice converts to PNG → embedded in docx.
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

SVG_SYSTEM_PROMPT = """You create simple, 2D black-and-white technical line drawings for GCSE exam papers.

RULES — follow ALL of these with NO exceptions:

1. OUTPUT: Return ONLY valid SVG code. Nothing else. No explanation, no markdown
   code fences. Start with <svg and end with </svg>.

2. CANVAS: viewBox="0 0 800 600". The entire diagram MUST fit inside this area
   with at least 40px padding on all sides. Nothing may extend beyond the viewBox.

3. STYLE — this is a technical line drawing, NOT an illustration:
   - Thin black outlines ONLY (stroke-width: 1.5px)
   - Fill: white (#ffffff) for ALL enclosed shapes — no grey, no colour, no patterns
   - Solid white background
   - NO shading, NO gradients, NO 3D effects, NO textures, NO shadows
   - NO decorative elements, NO borders around the diagram
   - High contrast: black lines on pure white

4. NO TEXT OR LABELS:
   - Do NOT include ANY text, letters, numbers, labels, or annotations
   - Do NOT include leader lines or label lines
   - The diagram is ONLY shapes and lines — students will add their own labels
   - The ONLY exception: single letters inside circuit symbols (A for ammeter,
     V for voltmeter) as these are part of the BSI symbol itself

5. CONTENT — draw ONLY what is described:
   - If the description says "cell wall, nucleus, and vacuole" draw ONLY those three
   - Do NOT add extra structures, organelles, vessels, or parts not mentioned
   - Do NOT add anything "for completeness" — only what is explicitly asked for

6. SIMPLICITY:
   - Minimalist style — fewest possible lines to represent each structure
   - Clean, uncluttered layout with generous spacing between parts
   - Each structure should be clearly distinct and separate from others
   - Think: the simplest possible diagram a teacher would draw on a whiteboard

7. ACCURACY:
   - Scientifically correct shapes and proportions for what IS shown
   - Circuit diagrams: correct BSI symbols (cell = two parallel lines long/short,
     resistor = rectangle, lamp = circle with X, ammeter = circle with A,
     voltmeter = circle with V, switch = break in line with dot)

8. ARROWS: If direction arrows are needed, use simple triangle arrowheads defined
   in <defs><marker>. Keep arrows thin and clean.

9. NO external images, NO embedded raster data, NO href links, NO <image> tags."""


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
        f"A simple, 2D black-and-white technical line drawing of: {description}\n\n"
        "Minimalist style, thin black outlines, no shading, no 3D effects, "
        "no textures, solid white background. Professional GCSE exam paper "
        "diagram style. High contrast. NO text or labels of any kind."
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

        # Post-process: strip any text elements that slipped through
        svg_content = _strip_text_elements(svg_content)

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


def _strip_text_elements(svg_content):
    """
    Remove any <text> elements from SVG as a safety net.

    Preserves text inside circuit symbols (single letter like A or V)
    by only stripping text elements with more than 1 character of content.
    """
    # Remove <text> elements with content longer than 1 char
    # This keeps "A" in ammeter circles but strips "Ammeter", "Cell wall" etc.
    svg_content = re.sub(
        r"<text[^>]*>[^<]{2,}</text>",
        "",
        svg_content,
    )
    # Also remove any standalone <line> elements that look like leader lines
    # (lines that end near where text was — heuristic: very thin lines)
    return svg_content


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
