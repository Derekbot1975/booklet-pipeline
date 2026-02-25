# Booklet Pipeline

An AI-powered system for generating structured curriculum booklets, initially designed for use in supervised study environments where students work independently without a specialist teacher present.

## What it does

- Parses a school's **scheme of work** (uploaded as an Excel spreadsheet) for any subject
- Uses the **Claude API** (Anthropic) to generate a complete, structured booklet for each lesson
- Produces booklets in **Word (.docx)** and **PDF** format
- Uploads finished booklets to **Google Drive** automatically
- Provides a **web dashboard** to manage courses, track progress, and generate booklets individually or in bulk

## Booklet structure

Every booklet follows a consistent format:
- **Knowledge Chunks** — focused blocks of essential content
- **Retrieval Practice Questions** — questions to check understanding
- **Worked Examples** — step-by-step model answers with full source material
- **Misconception Boxes** — common errors with corrections (highlighted in red)
- **Key Vocabulary** — subject-specific terms defined in context

## Tech stack

- **Backend:** Python / Flask
- **AI generation:** Anthropic Claude API (claude-sonnet) with prompt caching
- **Document generation:** python-docx + LibreOffice headless (PDF conversion)
- **Google integration:** Google Drive API v3 (OAuth 2.0)
- **Frontend:** Single-page HTML/CSS/JS dashboard

## Getting started

### Prerequisites
- Python 3.9+
- LibreOffice (for PDF conversion)
- An Anthropic API key
- A Google Cloud project with Drive API enabled (for Drive uploads)

### Setup

```bash
git clone https://github.com/Derekbot1975/booklet-pipeline.git
cd booklet-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in your API keys
python app.py
```

Open http://localhost:5050 in your browser.

### Environment variables

Create a `.env` file with the following:

```
ANTHROPIC_API_KEY=your_key_here
GDRIVE_ROOT_FOLDER_ID=your_google_drive_folder_id
```

Google Drive authentication uses OAuth 2.0 — you will be prompted to authenticate on first run.

## Features

- **Multi-course support** — manage Science, History, Geography and any other subject separately
- **Batch generation** — generate all booklets for a year group, subject, or key stage in one click
- **Update scheme of work** — upload a revised spreadsheet and the app detects what changed, cleans up old booklets, and resets progress for modified lessons
- **Export scheme of work** — export the full scheme as Excel, Word, PDF, Google Sheets, or Google Docs
- **Progress tracking** — tracks each lesson through generated → QA passed → uploaded to Drive
- **Consistent formatting** — heading hierarchy, coloured boxes, and layout enforced via a Booklet Formatting Specification

## Project status

Active development. Currently in prototype / internal review stage.

## Licence

MIT
