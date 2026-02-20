"""
DALL-E 3 diagram generation for self-study booklets.

Scans markdown content for [DRAWING SPACE: description] markers and
generates educational diagrams using OpenAI's DALL-E 3 API.
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


def get_openai_client():
    """Get an OpenAI client, or None if no key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-..."):
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception as e:
        logger.warning(f"Could not create OpenAI client: {e}")
        return None


def generate_diagram(description, output_path, size="1024x1024"):
    """
    Generate a single educational diagram using DALL-E 3.

    Args:
        description: what the diagram should show
        output_path: where to save the PNG
        size: image size (default 1024x1024)

    Returns:
        str path to saved image, or None on failure
    """
    client = get_openai_client()
    if not client:
        logger.info("No OpenAI API key configured — skipping diagram generation")
        return None

    prompt = (
        "Clean, educational scientific diagram suitable for a GCSE (age 14-16) "
        "science textbook. Black and white line drawing style with clear labels. "
        "No watermarks, no decorative elements, no background colour. "
        "Professional textbook quality. "
        f"Subject: {description}"
    )

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # Download and save the image
        import urllib.request
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(image_url, str(output_path))

        logger.info(f"Diagram generated: {output_path}")
        return str(output_path)

    except Exception as e:
        logger.warning(f"DALL-E diagram generation failed for '{description}': {e}")
        return None


def generate_diagrams_for_booklet(md_content, output_dir):
    """
    Scan markdown for [DRAWING SPACE: description] markers and generate
    diagrams for each one.

    Args:
        md_content: the markdown text
        output_dir: directory to save diagram images

    Returns:
        dict mapping description strings to image file paths
    """
    client = get_openai_client()
    if not client:
        logger.info("No OpenAI API key — skipping all diagram generation")
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
        logger.info(f"Generating diagram {idx + 1}/{len(unique_descriptions)}: {desc}")
        path = generate_diagram(desc, str(img_path))

        if path:
            result[desc] = path

        # Small delay between API calls to avoid rate limits
        if idx < len(unique_descriptions) - 1:
            time.sleep(1)

    logger.info(f"Generated {len(result)}/{len(unique_descriptions)} diagrams")
    return result
