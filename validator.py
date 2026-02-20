"""
Quality validation for generated booklet .docx files.

Runs automated checks matching the 60-second QC checklist from the production guide,
plus additional structural validation.
"""

import re
from pathlib import Path
from docx import Document


# Expected sections in a booklet (in rough order)
EXPECTED_SECTIONS = [
    "cover",           # Cover page info
    "recall",          # 20 recall questions
    "knowledge",       # Knowledge chunks (3-5)
    "summary",         # Summary box
    "sentence",        # Sentence starters
    "exam",            # Exam-style questions
    "mark_scheme",     # Mark schemes
    "self_assessment", # Self-assessment grid
]

# Keywords that indicate each section
SECTION_KEYWORDS = {
    "cover": ["self-study booklet", "lesson", "specification"],
    "recall": ["recall", "starter", "one-word", "holistic"],
    "knowledge": ["knowledge chunk", "key vocabulary", "worked example", "misconception", "knowledge check"],
    "summary": ["summary"],
    "sentence": ["sentence starter"],
    "exam": ["exam-style", "exam style", "exam question"],
    "mark_scheme": ["mark scheme", "answer key", "model answer", "grade 4", "grade 7", "grade 9"],
    "self_assessment": ["self-assessment", "self assessment", "score", "total marks"],
}


def validate_docx(docx_path):
    """
    Validate a generated booklet .docx file.

    Args:
        docx_path: path to the .docx file

    Returns:
        dict with:
            'valid': bool — overall pass/fail
            'score': int — number of checks passed
            'total': int — total number of checks
            'checks': list of check result dicts
            'warnings': list of warning strings
    """
    docx_path = Path(docx_path)
    checks = []
    warnings = []

    # Check 1: File exists and opens
    try:
        doc = Document(str(docx_path))
        checks.append({"name": "file_opens", "passed": True, "detail": "File opens correctly"})
    except Exception as e:
        checks.append({"name": "file_opens", "passed": False, "detail": f"Failed to open: {e}"})
        return {
            "valid": False,
            "score": 0,
            "total": 1,
            "checks": checks,
            "warnings": ["File could not be opened — all other checks skipped"],
        }

    # Check 2: File size reasonable (10-100 KB for docx)
    size_kb = docx_path.stat().st_size / 1024
    size_ok = 5 < size_kb < 200
    checks.append({
        "name": "file_size",
        "passed": size_ok,
        "detail": f"File size: {size_kb:.1f} KB (expected 5-200 KB)",
    })
    if not size_ok:
        warnings.append(f"Unusual file size: {size_kb:.1f} KB")

    # Extract all text for analysis
    full_text = "\n".join(p.text for p in doc.paragraphs)
    full_text_lower = full_text.lower()

    # Also check tables
    table_text = ""
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                table_text += cell.text + " "
    combined_text = full_text_lower + " " + table_text.lower()

    # Check 3: Has enough content (word count)
    word_count = len(full_text.split())
    content_ok = word_count > 500
    checks.append({
        "name": "word_count",
        "passed": content_ok,
        "detail": f"Word count: {word_count} (minimum 500)",
    })

    # Check 4: Paragraph count
    para_count = len([p for p in doc.paragraphs if p.text.strip()])
    para_ok = para_count > 20
    checks.append({
        "name": "paragraph_count",
        "passed": para_ok,
        "detail": f"Non-empty paragraphs: {para_count} (minimum 20)",
    })

    # Check 5: Has tables (for mark schemes, grids, etc.)
    table_count = len(doc.tables)
    tables_ok = table_count >= 1
    checks.append({
        "name": "has_tables",
        "passed": tables_ok,
        "detail": f"Tables found: {table_count} (minimum 1)",
    })

    # Check 6: Section detection — look for each expected section
    sections_found = {}
    for section, keywords in SECTION_KEYWORDS.items():
        found = any(kw in combined_text for kw in keywords)
        sections_found[section] = found

    # Check 6a: Recall questions section
    checks.append({
        "name": "has_recall",
        "passed": sections_found.get("recall", False),
        "detail": "Recall starter section " + ("found" if sections_found.get("recall") else "NOT found"),
    })

    # Check 6b: Knowledge chunks
    # Count how many "knowledge chunk" or "chunk" headers exist
    chunk_matches = re.findall(r"knowledge\s+chunk|chunk\s+\d", combined_text)
    chunk_count = len(chunk_matches)
    chunks_ok = chunk_count >= 2 or sections_found.get("knowledge", False)
    checks.append({
        "name": "has_knowledge_chunks",
        "passed": chunks_ok,
        "detail": f"Knowledge chunk indicators: {chunk_count}" + (" (section keywords found)" if sections_found.get("knowledge") else ""),
    })

    # Check 6c: Exam questions
    checks.append({
        "name": "has_exam_questions",
        "passed": sections_found.get("exam", False),
        "detail": "Exam-style questions section " + ("found" if sections_found.get("exam") else "NOT found"),
    })

    # Check 6d: Mark schemes
    checks.append({
        "name": "has_mark_schemes",
        "passed": sections_found.get("mark_scheme", False),
        "detail": "Mark schemes " + ("found" if sections_found.get("mark_scheme") else "NOT found"),
    })

    # Check 6e: Self-assessment
    checks.append({
        "name": "has_self_assessment",
        "passed": sections_found.get("self_assessment", False),
        "detail": "Self-assessment grid " + ("found" if sections_found.get("self_assessment") else "NOT found"),
    })

    # Check 6f: Summary box
    checks.append({
        "name": "has_summary",
        "passed": sections_found.get("summary", False),
        "detail": "Summary section " + ("found" if sections_found.get("summary") else "NOT found"),
    })

    # Check 6g: Sentence starters
    checks.append({
        "name": "has_sentence_starters",
        "passed": sections_found.get("sentence", False),
        "detail": "Sentence starters " + ("found" if sections_found.get("sentence") else "NOT found"),
    })

    # Check 7: Has headings (proper structure)
    heading_count = sum(
        1 for p in doc.paragraphs
        if p.style and p.style.name and p.style.name.startswith("Heading")
    )
    headings_ok = heading_count >= 5
    checks.append({
        "name": "has_headings",
        "passed": headings_ok,
        "detail": f"Headings found: {heading_count} (minimum 5)",
    })

    # Check 8: Misconception boxes present
    misconception_found = "misconception" in combined_text
    checks.append({
        "name": "has_misconceptions",
        "passed": misconception_found,
        "detail": "Misconception content " + ("found" if misconception_found else "NOT found"),
    })

    # Check 9: Worked examples present
    worked_found = "worked example" in combined_text or "example" in combined_text
    checks.append({
        "name": "has_worked_examples",
        "passed": worked_found,
        "detail": "Worked examples " + ("found" if worked_found else "NOT found"),
    })

    # Summary
    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    valid = passed >= total * 0.7  # 70% threshold

    return {
        "valid": valid,
        "score": passed,
        "total": total,
        "checks": checks,
        "warnings": warnings,
        "sections_found": sections_found,
    }


def validate_markdown(md_path):
    """
    Quick validation on markdown content before docx conversion.
    Useful for checking Claude API output before investing in conversion.
    """
    md_path = Path(md_path)
    content = md_path.read_text()
    content_lower = content.lower()

    checks = []

    # Length check
    word_count = len(content.split())
    checks.append({
        "name": "word_count",
        "passed": word_count > 1000,
        "detail": f"Word count: {word_count} (minimum 1000 for markdown)",
    })

    # Section checks
    for section, keywords in SECTION_KEYWORDS.items():
        found = any(kw in content_lower for kw in keywords)
        checks.append({
            "name": f"section_{section}",
            "passed": found,
            "detail": f"{section}: {'found' if found else 'NOT found'}",
        })

    # Table check (markdown tables)
    table_lines = [l for l in content.split("\n") if l.strip().startswith("|")]
    checks.append({
        "name": "has_tables",
        "passed": len(table_lines) > 5,
        "detail": f"Table lines: {len(table_lines)}",
    })

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)

    return {
        "valid": passed >= total * 0.7,
        "score": passed,
        "total": total,
        "checks": checks,
    }
