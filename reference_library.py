"""
Reference Document Library for the Booklet Pipeline.

Manages the school's reference documents that inform AI generation:
  - Expert input files (per subject)
  - National Curriculum documents (per subject + key stage)
  - KS4/5 specifications (per exam board + subject)
  - Scheme of Work exemplar format
  - Great Lesson / Great Booklet codification

Documents are stored in data/reference-docs/{id}/ with:
  - metadata.json  — category, subject, key_stage, exam_board, title, etc.
  - original file   — the uploaded .docx, .pdf, or .xlsx
  - parsed.txt      — AI-extracted plain text content

The parsed content is injected into Claude prompts as context for quality assurance.
"""

import hashlib
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).parent / "data" / "reference-docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Valid categories
CATEGORIES = {
    "expert_input": "Expert Input Files",
    "national_curriculum": "National Curriculum",
    "ks4_spec": "KS4/5 Specifications",
    "sow_exemplar": "Scheme of Work Exemplar Format",
    "great_lesson_code": "Great Lesson / Great Booklet Codification",
}

VALID_EXTENSIONS = {".docx", ".pdf", ".xlsx", ".xls", ".txt", ".md"}


def _doc_dir(doc_id):
    """Get the directory for a specific document."""
    return DOCS_DIR / doc_id


def _meta_path(doc_id):
    """Get the metadata file path for a document."""
    return _doc_dir(doc_id) / "metadata.json"


def _parsed_path(doc_id):
    """Get the parsed content file path for a document."""
    return _doc_dir(doc_id) / "parsed.txt"


def _file_hash(filepath):
    """Compute SHA-256 hash of a file for change detection."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def list_documents(category=None, subject=None, key_stage=None):
    """List all reference documents, optionally filtered."""
    docs = []
    for d in sorted(DOCS_DIR.iterdir()):
        meta_file = d / "metadata.json"
        if not meta_file.exists():
            continue
        try:
            meta = json.loads(meta_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        if category and meta.get("category") != category:
            continue
        if subject and meta.get("subject") != subject:
            continue
        if key_stage and meta.get("key_stage") != key_stage:
            continue

        # Add parsed status
        meta["has_parsed_content"] = _parsed_path(meta["id"]).exists()
        docs.append(meta)

    return docs


def get_document(doc_id):
    """Get a single document's metadata and parsed content."""
    meta_file = _meta_path(doc_id)
    if not meta_file.exists():
        return None

    meta = json.loads(meta_file.read_text())
    parsed_file = _parsed_path(doc_id)
    if parsed_file.exists():
        meta["parsed_content"] = parsed_file.read_text()
    else:
        meta["parsed_content"] = None
    meta["has_parsed_content"] = parsed_file.exists()
    return meta


def save_document(file_path, category, title, subject=None, key_stage=None,
                  exam_board=None, description=None, doc_id=None):
    """
    Save a reference document. Copies the file, stores metadata,
    and parses content.

    Args:
        file_path: Path to the uploaded file
        category: One of the CATEGORIES keys
        title: Human-readable title
        subject: Optional subject (e.g. "Science", "History")
        key_stage: Optional key stage (e.g. "KS3", "KS4")
        exam_board: Optional exam board (e.g. "AQA", "Edexcel")
        description: Optional description
        doc_id: Optional existing ID (for replacement)

    Returns:
        Document metadata dict
    """
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of: {list(CATEGORIES.keys())}")

    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = src.suffix.lower()
    if ext not in VALID_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {VALID_EXTENSIONS}")

    # Generate or reuse ID
    if not doc_id:
        doc_id = str(uuid.uuid4())[:8]

    doc_dir = _doc_dir(doc_id)
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Copy file to doc directory
    import shutil
    dest_filename = f"document{ext}"
    dest_path = doc_dir / dest_filename
    shutil.copy2(str(src), str(dest_path))

    # Build metadata
    content_hash = _file_hash(str(dest_path))
    now = datetime.utcnow().isoformat()

    meta = {
        "id": doc_id,
        "category": category,
        "category_label": CATEGORIES[category],
        "subject": subject,
        "key_stage": key_stage,
        "exam_board": exam_board,
        "title": title,
        "description": description or "",
        "filename": src.name,
        "file_format": ext.lstrip("."),
        "file_path": str(dest_path),
        "content_hash": content_hash,
        "uploaded_at": now,
        "updated_at": now,
    }

    _meta_path(doc_id).write_text(json.dumps(meta, indent=2))

    # Parse the document content
    try:
        parsed = _parse_document(str(dest_path), ext)
        _parsed_path(doc_id).write_text(parsed)
        meta["has_parsed_content"] = True
        logger.info(f"Parsed reference doc '{title}' ({len(parsed)} chars)")
    except Exception as e:
        logger.error(f"Failed to parse reference doc '{title}': {e}")
        meta["has_parsed_content"] = False

    return meta


def update_document(doc_id, **kwargs):
    """Update metadata fields for an existing document."""
    meta_file = _meta_path(doc_id)
    if not meta_file.exists():
        raise ValueError(f"Document not found: {doc_id}")

    meta = json.loads(meta_file.read_text())

    allowed_fields = {"title", "description", "subject", "key_stage", "exam_board", "category"}
    for key, value in kwargs.items():
        if key in allowed_fields:
            meta[key] = value
            if key == "category" and value in CATEGORIES:
                meta["category_label"] = CATEGORIES[value]

    meta["updated_at"] = datetime.utcnow().isoformat()
    meta_file.write_text(json.dumps(meta, indent=2))
    return meta


def delete_document(doc_id):
    """Delete a reference document and all its files."""
    doc_dir = _doc_dir(doc_id)
    if not doc_dir.exists():
        raise ValueError(f"Document not found: {doc_id}")

    import shutil
    shutil.rmtree(str(doc_dir))
    return True


def reparse_document(doc_id):
    """Re-parse a document's content (e.g. after updating the parser)."""
    meta = get_document(doc_id)
    if not meta:
        raise ValueError(f"Document not found: {doc_id}")

    file_path = meta.get("file_path")
    if not file_path or not Path(file_path).exists():
        raise FileNotFoundError(f"Source file missing for document {doc_id}")

    ext = Path(file_path).suffix.lower()
    parsed = _parse_document(file_path, ext)
    _parsed_path(doc_id).write_text(parsed)
    return {"doc_id": doc_id, "parsed_length": len(parsed)}


def get_reference_context(subject=None, key_stage=None, exam_board=None):
    """
    Build the reference context string for AI prompts.

    Gathers all relevant reference documents and assembles them into a
    single context string that gets injected into Claude system prompts.

    Always includes: great_lesson_code and sow_exemplar (if available).
    Filters by subject, key_stage, and exam_board for other categories.
    """
    docs = list_documents()
    context_parts = []

    for doc in docs:
        doc_id = doc["id"]
        parsed_file = _parsed_path(doc_id)
        if not parsed_file.exists():
            continue
        content = parsed_file.read_text().strip()
        if not content:
            continue

        cat = doc.get("category")

        # Always include these cross-cutting documents
        if cat == "great_lesson_code":
            context_parts.append(
                f"=== SCHOOL QUALITY FRAMEWORK ===\n"
                f"Title: {doc.get('title', 'Quality Framework')}\n\n"
                f"{content}"
            )
        elif cat == "sow_exemplar":
            context_parts.append(
                f"=== SCHEME OF WORK FORMAT ===\n"
                f"Title: {doc.get('title', 'SoW Exemplar')}\n\n"
                f"{content}"
            )
        elif cat == "expert_input":
            # Match by subject
            if subject and doc.get("subject", "").lower() == subject.lower():
                context_parts.append(
                    f"=== EXPERT INPUT FOR {subject.upper()} ===\n"
                    f"Title: {doc.get('title', 'Expert Input')}\n\n"
                    f"{content}"
                )
        elif cat == "national_curriculum":
            # Match by subject AND key stage
            doc_subj = (doc.get("subject") or "").lower()
            doc_ks = (doc.get("key_stage") or "").upper()
            if subject and doc_subj == subject.lower():
                if not key_stage or doc_ks == key_stage.upper():
                    ks_label = doc_ks or ""
                    context_parts.append(
                        f"=== NATIONAL CURRICULUM ({ks_label} {subject}) ===\n"
                        f"Title: {doc.get('title', 'National Curriculum')}\n\n"
                        f"{content}"
                    )
        elif cat == "ks4_spec":
            # Match by subject and optionally exam board
            doc_subj = (doc.get("subject") or "").lower()
            doc_board = (doc.get("exam_board") or "").lower()
            if subject and doc_subj == subject.lower():
                if not exam_board or doc_board == exam_board.lower():
                    board_label = doc.get("exam_board") or "Unknown"
                    context_parts.append(
                        f"=== SPECIFICATION ({board_label} {subject}) ===\n"
                        f"Title: {doc.get('title', 'Specification')}\n\n"
                        f"{content}"
                    )

    if not context_parts:
        return ""

    return "\n\n---\n\n".join(context_parts)


# ───────────────────────────────────────────────────────────────────
# Document parsing — extract text from uploaded files
# ───────────────────────────────────────────────────────────────────

def _parse_document(file_path, ext):
    """Parse a document to extract its text content."""
    ext = ext.lower()
    if ext in (".txt", ".md"):
        return Path(file_path).read_text(encoding="utf-8")
    elif ext == ".docx":
        return _parse_docx(file_path)
    elif ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext in (".xlsx", ".xls"):
        return _parse_excel(file_path)
    else:
        raise ValueError(f"Cannot parse file type: {ext}")


def _parse_docx(file_path):
    """Extract text from a .docx file."""
    try:
        from docx import Document
        doc = Document(file_path)
        parts = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                # Preserve heading structure
                if para.style and para.style.name.startswith("Heading"):
                    level = para.style.name.replace("Heading ", "").strip()
                    try:
                        level_num = int(level)
                        parts.append(f"{'#' * level_num} {text}")
                    except ValueError:
                        parts.append(text)
                else:
                    parts.append(text)

        # Also extract table content
        for table in doc.tables:
            rows = []
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                rows.append(" | ".join(cells))
            if rows:
                parts.append("\n".join(rows))

        return "\n\n".join(parts)
    except Exception as e:
        logger.error(f"DOCX parse failed: {e}")
        return f"[Parse error: {e}]"


def _parse_pdf(file_path):
    """Extract text from a PDF file using available libraries."""
    # Try PyPDF2 first (most common)
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    parts.append(text.strip())
            return "\n\n---\n\n".join(parts)
    except ImportError:
        pass

    # Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    parts.append(text.strip())
            return "\n\n---\n\n".join(parts)
    except ImportError:
        pass

    # Fallback: try to use subprocess with pdftotext
    try:
        import subprocess
        result = subprocess.run(
            ["pdftotext", "-layout", file_path, "-"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return "[PDF parsing requires PyPDF2 or pdfplumber. Install with: pip install PyPDF2]"


def _parse_excel(file_path):
    """Extract text from an Excel spreadsheet."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        parts = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            parts.append(f"## Sheet: {sheet_name}")
            rows = []
            for row in ws.iter_rows(values_only=True):
                cells = [str(c).strip() if c is not None else "" for c in row]
                if any(cells):
                    rows.append(" | ".join(cells))
            parts.append("\n".join(rows))
        wb.close()
        return "\n\n".join(parts)
    except Exception as e:
        logger.error(f"Excel parse failed: {e}")
        return f"[Excel parse error: {e}]"
