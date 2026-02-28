#!/usr/bin/env python3
"""
Download National Curriculum and Exam Specifications

Downloads:
1. DfE National Curriculum programmes of study (EYFS–KS3) from GOV.UK
2. GCSE and A Level specifications from AQA, Edexcel, OCR, WJEC/Eduqas

All PDFs are saved to data/specs-and-nc/ and imported into the Reference Library
with correct metadata so they're automatically used in scheme generation.

Usage:
    python download_specs.py                   # Download everything
    python download_specs.py --nc-only         # Just National Curriculum
    python download_specs.py --specs-only      # Just exam specs
    python download_specs.py --subject science  # One subject only
    python download_specs.py --import          # Import downloaded files into Reference Library
    python download_specs.py --list            # Show what would be downloaded
"""

import argparse
import json
import os
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# ─────────────────────────────────────────────────────────────
# OUTPUT DIRECTORY
# ─────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "data" / "specs-and-nc"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NC_DIR = OUTPUT_DIR / "national-curriculum"
NC_DIR.mkdir(parents=True, exist_ok=True)

SPECS_DIR = OUTPUT_DIR / "specifications"
SPECS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# SUBJECT MAPPING
# Maps our internal subject names to how each board refers to them
# ─────────────────────────────────────────────────────────────

# National Curriculum documents from GOV.UK
# These are the statutory programmes of study PDFs
NC_DOCUMENTS = {
    # Each entry has separate "files" for primary and secondary PDFs
    "Science": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a806ebd40f0b62305b8b1fa/PRIMARY_national_curriculum_-_Science.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_science_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7d563de5274a2af0ae2ffa/SECONDARY_national_curriculum_-_Science_220714.pdf", "key_stages": ["KS3"], "filename": "nc_science_secondary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7efc65ed915d74e33f3ac9/Science_KS4_PoS_7_November_2014.pdf", "key_stages": ["KS4"], "filename": "nc_science_ks4.pdf"},
    ]},
    "Mathematics": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7da548ed915d2ac884cb07/PRIMARY_national_curriculum_-_Mathematics_220714.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_maths_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c1408e5274a1f5cc75a68/SECONDARY_national_curriculum_-_Mathematics.pdf", "key_stages": ["KS3"], "filename": "nc_maths_secondary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7dc9dced915d2ac884d8ef/KS4_maths_PoS_FINAL_170714.pdf", "key_stages": ["KS4"], "filename": "nc_maths_ks4.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c5b95e5274a7ee501a6e5/Mathematics_Appendix_1.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_maths_appendix1.pdf"},
    ]},
    "English": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7de93840f0b62305b7f8ee/PRIMARY_national_curriculum_-_English_220714.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_english_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7b8761ed915d4147620f6b/SECONDARY_national_curriculum_-_English2.pdf", "key_stages": ["KS3"], "filename": "nc_english_secondary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7585a1ed915d731495a9dd/KS4_English_PoS_FINAL_170714.pdf", "key_stages": ["KS4"], "filename": "nc_english_ks4.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7ccc06ed915d63cc65ce61/English_Appendix_1_-_Spelling.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_english_appendix1_spelling.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7d913aed915d3fb959486f/English_Appendix_2_-_Vocabulary_grammar_and_punctuation.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_english_appendix2_vocab.pdf"},
    ]},
    "History": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c2917e5274a1f5cc762cf/PRIMARY_national_curriculum_-_History.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_history_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c66d740f0b626628abcdd/SECONDARY_national_curriculum_-_History.pdf", "key_stages": ["KS3"], "filename": "nc_history_secondary.pdf"},
    ]},
    "Geography": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c1ecae5274a1f5cc75e97/PRIMARY_national_curriculum_-_Geography.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_geography_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7b8699ed915d131105fd16/SECONDARY_national_curriculum_-_Geography.pdf", "key_stages": ["KS3"], "filename": "nc_geography_secondary.pdf"},
    ]},
    "Computing": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c576be5274a1b00423213/PRIMARY_national_curriculum_-_Computing.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_computing_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7cb981ed915d682236228d/SECONDARY_national_curriculum_-_Computing.pdf", "key_stages": ["KS3", "KS4"], "filename": "nc_computing_secondary.pdf"},
    ]},
    "Art and Design": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7ba810ed915d4147621ca0/PRIMARY_national_curriculum_-_Art_and_design.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_art_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c4e02ed915d3d0e87b798/SECONDARY_national_curriculum_-_Art_and_design.pdf", "key_stages": ["KS3"], "filename": "nc_art_secondary.pdf"},
    ]},
    "Music": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7b7f8c40f0b645ba3c4b8a/PRIMARY_national_curriculum_-_Music.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_music_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c869440f0b62aff6c2499/SECONDARY_national_curriculum_-_Music.pdf", "key_stages": ["KS3"], "filename": "nc_music_secondary.pdf"},
    ]},
    "Physical Education": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c4edfed915d3d0e87b801/PRIMARY_national_curriculum_-_Physical_education.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_pe_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c74e2e5274a5255bcec5f/SECONDARY_national_curriculum_-_Physical_education.pdf", "key_stages": ["KS3", "KS4"], "filename": "nc_pe_secondary.pdf"},
    ]},
    "Design and Technology": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7ca43640f0b6629523adc1/PRIMARY_national_curriculum_-_Design_and_technology.pdf", "key_stages": ["KS1", "KS2"], "filename": "nc_dt_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c99ebed915d6969f46087/SECONDARY_national_curriculum_-_Design_and_technology.pdf", "key_stages": ["KS3"], "filename": "nc_dt_secondary.pdf"},
    ]},
    "Modern Foreign Languages": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5a7b9246e5274a7318b8f889/PRIMARY_national_curriculum_-_Languages.pdf", "key_stages": ["KS2"], "filename": "nc_mfl_primary.pdf"},
        {"url": "https://assets.publishing.service.gov.uk/media/5a7c5afae5274a7ee501a69e/SECONDARY_national_curriculum_-_Languages.pdf", "key_stages": ["KS3"], "filename": "nc_mfl_secondary.pdf"},
    ]},
    "Citizenship": {"files": [
        {"url": "https://assets.publishing.service.gov.uk/media/5f324f7ad3bf7f1b1ea28dca/SECONDARY_national_curriculum_-_Citizenship.pdf", "key_stages": ["KS3", "KS4"], "filename": "nc_citizenship_secondary.pdf"},
    ]},
}

# Exam board specifications
# Format: {subject_key: {board: {level: {url, filename, subject_name}}}}
EXAM_SPECS = {
    "Science": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Combined Science: Trilogy",
                "url": "https://filestore.aqa.org.uk/resources/science/specifications/AQA-8464-SP-2016.PDF",
                "filename": "aqa_gcse_combined_science_trilogy.pdf",
            },
            "A Level Biology": {
                "name": "AQA A Level Biology",
                "url": "https://filestore.aqa.org.uk/resources/biology/specifications/AQA-7401-7402-SP-2015.PDF",
                "filename": "aqa_alevel_biology.pdf",
            },
            "A Level Chemistry": {
                "name": "AQA A Level Chemistry",
                "url": "https://filestore.aqa.org.uk/resources/chemistry/specifications/AQA-7404-7405-SP-2015.PDF",
                "filename": "aqa_alevel_chemistry.pdf",
            },
            "A Level Physics": {
                "name": "AQA A Level Physics",
                "url": "https://filestore.aqa.org.uk/resources/physics/specifications/AQA-7407-7408-SP-2015.PDF",
                "filename": "aqa_alevel_physics.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Combined Science",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-combined-science/Specification-GCSE-L1-L2-in-Combined-Science.pdf",
                "filename": "edexcel_gcse_combined_science.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Combined Science A (Gateway)",
                "url": "https://www.ocr.org.uk/Images/234598-specification-accredited-gcse-combined-science-a-gateway-science-suite-j250.pdf",
                "filename": "ocr_gcse_combined_science.pdf",
            },
        },
    },
    "Mathematics": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Mathematics",
                "url": "https://filestore.aqa.org.uk/resources/mathematics/specifications/AQA-8300-SP-2015.PDF",
                "filename": "aqa_gcse_maths.pdf",
            },
            "A Level": {
                "name": "AQA A Level Mathematics",
                "url": "https://filestore.aqa.org.uk/resources/mathematics/specifications/AQA-7357-SP-2017.PDF",
                "filename": "aqa_alevel_maths.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Mathematics (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-mathematics-2015/Specification-Level-1-Level-2-GCSE-9-to-1-in-Mathematics-1MA1.pdf",
                "filename": "edexcel_gcse_maths.pdf",
            },
            "A Level": {
                "name": "Edexcel A Level Mathematics",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/a-level-mathematics-2017/Specification-GCE-Mathematics-8MA0-9MA0.pdf",
                "filename": "edexcel_alevel_maths.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Mathematics (9-1)",
                "url": "https://www.ocr.org.uk/Images/168982-specification-gcse-mathematics-j560.pdf",
                "filename": "ocr_gcse_maths.pdf",
            },
        },
    },
    "English": {
        "AQA": {
            "GCSE Language": {
                "name": "AQA GCSE English Language",
                "url": "https://filestore.aqa.org.uk/resources/english/specifications/AQA-8700-SP-2015.PDF",
                "filename": "aqa_gcse_english_language.pdf",
            },
            "GCSE Literature": {
                "name": "AQA GCSE English Literature",
                "url": "https://filestore.aqa.org.uk/resources/english/specifications/AQA-8702-SP-2015.PDF",
                "filename": "aqa_gcse_english_literature.pdf",
            },
            "A Level Language": {
                "name": "AQA A Level English Language",
                "url": "https://filestore.aqa.org.uk/resources/english/specifications/AQA-7701-7702-SP-2015.PDF",
                "filename": "aqa_alevel_english_language.pdf",
            },
            "A Level Literature": {
                "name": "AQA A Level English Literature A",
                "url": "https://filestore.aqa.org.uk/resources/english/specifications/AQA-7711-7712-SP-2015.PDF",
                "filename": "aqa_alevel_english_literature.pdf",
            },
        },
        "Edexcel": {
            "GCSE Language": {
                "name": "Edexcel GCSE English Language",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-english-language-2015/Specification-GCSE-L1-L2-in-English-Language.pdf",
                "filename": "edexcel_gcse_english_language.pdf",
            },
            "GCSE Literature": {
                "name": "Edexcel GCSE English Literature",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-english-literature-2015/Specification-GCSE-L1-L2-in-English-Literature.pdf",
                "filename": "edexcel_gcse_english_literature.pdf",
            },
        },
        "OCR": {
            "GCSE Language": {
                "name": "OCR GCSE English Language (9-1)",
                "url": "https://www.ocr.org.uk/Images/168985-specification-gcse-english-language-j351.pdf",
                "filename": "ocr_gcse_english_language.pdf",
            },
        },
    },
    "History": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE History",
                "url": "https://filestore.aqa.org.uk/resources/history/specifications/AQA-8145-SP-2016.PDF",
                "filename": "aqa_gcse_history.pdf",
            },
            "A Level": {
                "name": "AQA A Level History",
                "url": "https://filestore.aqa.org.uk/resources/history/specifications/AQA-7041-7042-SP-2015.PDF",
                "filename": "aqa_alevel_history.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE History (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-history-2016/Specification-GCSE-L1-L2-in-History-2016.pdf",
                "filename": "edexcel_gcse_history.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE History A (Explaining the Modern World)",
                "url": "https://www.ocr.org.uk/Images/207165-specification-accredited-gcse-history-a-j410.pdf",
                "filename": "ocr_gcse_history.pdf",
            },
        },
    },
    "Geography": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Geography",
                "url": "https://filestore.aqa.org.uk/resources/geography/specifications/AQA-8035-SP-2016.PDF",
                "filename": "aqa_gcse_geography.pdf",
            },
            "A Level": {
                "name": "AQA A Level Geography",
                "url": "https://filestore.aqa.org.uk/resources/geography/specifications/AQA-7037-SP-2016.PDF",
                "filename": "aqa_alevel_geography.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Geography A",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-geography-a-2016/Specification-GCSE-L1-L2-in-Geography-A.pdf",
                "filename": "edexcel_gcse_geography.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Geography A (Geographical Themes)",
                "url": "https://www.ocr.org.uk/Images/207307-specification-accredited-gcse-geography-a-geographical-themes-j383.pdf",
                "filename": "ocr_gcse_geography.pdf",
            },
        },
    },
    "Religious Studies": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Religious Studies A",
                "url": "https://filestore.aqa.org.uk/resources/rs/specifications/AQA-8062-SP-2016.PDF",
                "filename": "aqa_gcse_rs.pdf",
            },
            "A Level": {
                "name": "AQA A Level Religious Studies",
                "url": "https://filestore.aqa.org.uk/resources/rs/specifications/AQA-7061-7062-SP-2016.PDF",
                "filename": "aqa_alevel_rs.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Religious Studies A",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-religious-studies-a-2016/Specification-GCSE-L1-L2-in-Religious-Studies-A.pdf",
                "filename": "edexcel_gcse_rs.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Religious Studies (9-1)",
                "url": "https://www.ocr.org.uk/Images/242488-specification-gcse-religious-studies-j625.pdf",
                "filename": "ocr_gcse_rs.pdf",
            },
        },
    },
    "Computing": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Computer Science",
                "url": "https://filestore.aqa.org.uk/resources/computing/specifications/AQA-8525-SP-2020.PDF",
                "filename": "aqa_gcse_computer_science.pdf",
            },
            "A Level": {
                "name": "AQA A Level Computer Science",
                "url": "https://filestore.aqa.org.uk/resources/computing/specifications/AQA-7516-7517-SP-2015.PDF",
                "filename": "aqa_alevel_computer_science.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Computer Science (9-1)",
                "url": "https://www.ocr.org.uk/Images/558027-specification-gcse-computer-science-j277.pdf",
                "filename": "ocr_gcse_computer_science.pdf",
            },
            "A Level": {
                "name": "OCR A Level Computer Science",
                "url": "https://www.ocr.org.uk/Images/170844-specification-accredited-a-level-gce-computer-science-h446.pdf",
                "filename": "ocr_alevel_computer_science.pdf",
            },
        },
    },
    "Art and Design": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Art and Design",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCSE-SP-2015.PDF",
                "filename": "aqa_gcse_art.pdf",
            },
            "A Level": {
                "name": "AQA A Level Art and Design",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCE-W-SP-2015.PDF",
                "filename": "aqa_alevel_art.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Art and Design",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-art-and-design-2016/Specification-GCSE-L1-L2-in-Art-and-Design.pdf",
                "filename": "edexcel_gcse_art.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Art and Design",
                "url": "https://www.ocr.org.uk/Images/225403-specification-accredited-gcse-art-and-design-j170-j176.pdf",
                "filename": "ocr_gcse_art.pdf",
            },
        },
    },
    "Music": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Music",
                "url": "https://filestore.aqa.org.uk/resources/music/specifications/AQA-8271-SP-2016.PDF",
                "filename": "aqa_gcse_music.pdf",
            },
            "A Level": {
                "name": "AQA A Level Music",
                "url": "https://filestore.aqa.org.uk/resources/music/specifications/AQA-7272-SP-2016.PDF",
                "filename": "aqa_alevel_music.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Music (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-music-2016/Specification-GCSE-L1-L2-in-Music.pdf",
                "filename": "edexcel_gcse_music.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Music (9-1)",
                "url": "https://www.ocr.org.uk/Images/208823-specification-accredited-gcse-music-j536.pdf",
                "filename": "ocr_gcse_music.pdf",
            },
        },
    },
    "Physical Education": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Physical Education",
                "url": "https://filestore.aqa.org.uk/resources/pe/specifications/AQA-8582-SP-2016.PDF",
                "filename": "aqa_gcse_pe.pdf",
            },
            "A Level": {
                "name": "AQA A Level Physical Education",
                "url": "https://filestore.aqa.org.uk/resources/pe/specifications/AQA-7582-SP-2016.PDF",
                "filename": "aqa_alevel_pe.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Physical Education (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-physical-education-2016/Specification-GCSE-L1-L2-in-Physical-Education.pdf",
                "filename": "edexcel_gcse_pe.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Physical Education (9-1)",
                "url": "https://www.ocr.org.uk/Images/234822-specification-accredited-gcse-physical-education-j587.pdf",
                "filename": "ocr_gcse_pe.pdf",
            },
        },
    },
    "Drama": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Drama",
                "url": "https://filestore.aqa.org.uk/resources/drama/specifications/AQA-8261-SP-2016.PDF",
                "filename": "aqa_gcse_drama.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Drama (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-drama-2016/Specification-GCSE-L1-L2-in-Drama.pdf",
                "filename": "edexcel_gcse_drama.pdf",
            },
            "A Level": {
                "name": "Edexcel A Level Drama and Theatre",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/a-level-drama-and-theatre-2016/Specification-GCE-AS-and-A-Level-in-Drama-and-Theatre.pdf",
                "filename": "edexcel_alevel_drama.pdf",
            },
        },
    },
    "Design and Technology": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Design and Technology",
                "url": "https://filestore.aqa.org.uk/resources/design-and-technology/specifications/AQA-8552-SP-2017.PDF",
                "filename": "aqa_gcse_dt.pdf",
            },
            "A Level": {
                "name": "AQA A Level Design and Technology: Product Design",
                "url": "https://filestore.aqa.org.uk/resources/design-and-technology/specifications/AQA-7552-SP-2017.PDF",
                "filename": "aqa_alevel_dt.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Design and Technology (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-design-and-technology-2017/Specification-GCSE-L1-L2-in-Design-and-Technology.pdf",
                "filename": "edexcel_gcse_dt.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Design and Technology (9-1)",
                "url": "https://www.ocr.org.uk/Images/304189-specification-accredited-gcse-design-and-technology-j310.pdf",
                "filename": "ocr_gcse_dt.pdf",
            },
        },
    },
    "Business Studies": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Business",
                "url": "https://filestore.aqa.org.uk/resources/business/specifications/AQA-8132-SP-2017.PDF",
                "filename": "aqa_gcse_business.pdf",
            },
            "A Level": {
                "name": "AQA A Level Business",
                "url": "https://filestore.aqa.org.uk/resources/business/specifications/AQA-7131-7132-SP-2015.PDF",
                "filename": "aqa_alevel_business.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Business (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-business-2017/Specification-GCSE-L1-L2-in-Business.pdf",
                "filename": "edexcel_gcse_business.pdf",
            },
            "A Level": {
                "name": "Edexcel A Level Business",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/a-level-business-2015/Specification-GCE-AS-and-A-Level-in-Business.pdf",
                "filename": "edexcel_alevel_business.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR GCSE Business (9-1)",
                "url": "https://www.ocr.org.uk/Images/304184-specification-accredited-gcse-business-j204.pdf",
                "filename": "ocr_gcse_business.pdf",
            },
        },
    },
    "Textiles": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Art and Design: Textile Design",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCSE-SP-2015.PDF",
                "filename": "aqa_gcse_textiles.pdf",
            },
        },
    },
    "Photography": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Art and Design: Photography",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCSE-SP-2015.PDF",
                "filename": "aqa_gcse_photography.pdf",
            },
            "A Level": {
                "name": "AQA A Level Art and Design: Photography",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCE-W-SP-2015.PDF",
                "filename": "aqa_alevel_photography.pdf",
            },
        },
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Art and Design: Photography",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-art-and-design-2016/Specification-GCSE-L1-L2-in-Art-and-Design.pdf",
                "filename": "edexcel_gcse_photography.pdf",
            },
        },
    },
    "3D Design": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Art and Design: 3D Design",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCSE-SP-2015.PDF",
                "filename": "aqa_gcse_3d_design.pdf",
            },
            "A Level": {
                "name": "AQA A Level Art and Design: 3D Design",
                "url": "https://filestore.aqa.org.uk/resources/art-and-design/specifications/AQA-ART-GCE-W-SP-2015.PDF",
                "filename": "aqa_alevel_3d_design.pdf",
            },
        },
    },
    "Statistics": {
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE Statistics (9-1)",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-statistics-2017/Specification-GCSE-L1-L2-in-Statistics.pdf",
                "filename": "edexcel_gcse_statistics.pdf",
            },
        },
    },
    "Psychology": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Psychology",
                "url": "https://filestore.aqa.org.uk/resources/psychology/specifications/AQA-8182-SP-2017.PDF",
                "filename": "aqa_gcse_psychology.pdf",
            },
            "A Level": {
                "name": "AQA A Level Psychology",
                "url": "https://filestore.aqa.org.uk/resources/psychology/specifications/AQA-7181-7182-SP-2015.PDF",
                "filename": "aqa_alevel_psychology.pdf",
            },
        },
        "Edexcel": {
            "A Level": {
                "name": "Edexcel A Level Psychology",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/a-level-psychology-2015/Specification-GCE-AS-and-A-Level-in-Psychology.pdf",
                "filename": "edexcel_alevel_psychology.pdf",
            },
        },
        "OCR": {
            "A Level": {
                "name": "OCR A Level Psychology",
                "url": "https://www.ocr.org.uk/Images/171733-specification-accredited-a-level-gce-psychology-h567.pdf",
                "filename": "ocr_alevel_psychology.pdf",
            },
        },
    },
    "Sociology": {
        "AQA": {
            "GCSE": {
                "name": "AQA GCSE Sociology",
                "url": "https://filestore.aqa.org.uk/resources/sociology/specifications/AQA-8192-SP-2017.PDF",
                "filename": "aqa_gcse_sociology.pdf",
            },
            "A Level": {
                "name": "AQA A Level Sociology",
                "url": "https://filestore.aqa.org.uk/resources/sociology/specifications/AQA-7191-7192-SP-2015.PDF",
                "filename": "aqa_alevel_sociology.pdf",
            },
        },
        "OCR": {
            "A Level": {
                "name": "OCR A Level Sociology",
                "url": "https://www.ocr.org.uk/Images/170215-specification-accredited-a-level-gce-sociology-h580.pdf",
                "filename": "ocr_alevel_sociology.pdf",
            },
        },
    },
    "Economics": {
        "AQA": {
            "A Level": {
                "name": "AQA A Level Economics",
                "url": "https://filestore.aqa.org.uk/resources/economics/specifications/AQA-7135-7136-SP-2015.PDF",
                "filename": "aqa_alevel_economics.pdf",
            },
        },
        "Edexcel": {
            "A Level": {
                "name": "Edexcel A Level Economics A",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/a-level-economics-a-2015/Specification-GCE-AS-and-A-Level-in-Economics-A.pdf",
                "filename": "edexcel_alevel_economics.pdf",
            },
        },
        "OCR": {
            "A Level": {
                "name": "OCR A Level Economics",
                "url": "https://www.ocr.org.uk/Images/170844-specification-accredited-a-level-gce-economics-h460.pdf",
                "filename": "ocr_alevel_economics.pdf",
            },
        },
    },
    "Modern Foreign Languages": {
        "AQA": {
            "GCSE French": {
                "name": "AQA GCSE French",
                "url": "https://filestore.aqa.org.uk/resources/french/specifications/AQA-8658-SP-2016.PDF",
                "filename": "aqa_gcse_french.pdf",
            },
            "GCSE Spanish": {
                "name": "AQA GCSE Spanish",
                "url": "https://filestore.aqa.org.uk/resources/spanish/specifications/AQA-8698-SP-2016.PDF",
                "filename": "aqa_gcse_spanish.pdf",
            },
            "GCSE German": {
                "name": "AQA GCSE German",
                "url": "https://filestore.aqa.org.uk/resources/german/specifications/AQA-8668-SP-2016.PDF",
                "filename": "aqa_gcse_german.pdf",
            },
            "A Level French": {
                "name": "AQA A Level French",
                "url": "https://filestore.aqa.org.uk/resources/french/specifications/AQA-7652-SP-2016.PDF",
                "filename": "aqa_alevel_french.pdf",
            },
            "A Level Spanish": {
                "name": "AQA A Level Spanish",
                "url": "https://filestore.aqa.org.uk/resources/spanish/specifications/AQA-7692-SP-2016.PDF",
                "filename": "aqa_alevel_spanish.pdf",
            },
            "A Level German": {
                "name": "AQA A Level German",
                "url": "https://filestore.aqa.org.uk/resources/german/specifications/AQA-7662-SP-2016.PDF",
                "filename": "aqa_alevel_german.pdf",
            },
        },
        "Edexcel": {
            "GCSE French": {
                "name": "Edexcel GCSE French",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-french-2016/Specification-GCSE-L1-L2-in-French.pdf",
                "filename": "edexcel_gcse_french.pdf",
            },
            "GCSE Spanish": {
                "name": "Edexcel GCSE Spanish",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/gcse-spanish-2016/Specification-GCSE-L1-L2-in-Spanish.pdf",
                "filename": "edexcel_gcse_spanish.pdf",
            },
        },
    },
    "Information Technology": {
        "Edexcel": {
            "GCSE": {
                "name": "Edexcel GCSE ICT",
                "url": "https://qualifications.pearson.com/content/dam/secure/silver/btec-technicals-it/Specification-BTEC-Tech-Award-Digital-Information-Technology.pdf",
                "filename": "edexcel_btec_dit.pdf",
            },
        },
        "OCR": {
            "GCSE": {
                "name": "OCR Cambridge Nationals in IT",
                "url": "https://www.ocr.org.uk/Images/341025-specification-cambridge-nationals-information-technologies-j836.pdf",
                "filename": "ocr_nationals_it.pdf",
            },
        },
    },
}

# ─────────────────────────────────────────────────────────────
# SUBJECT NAME NORMALISATION
# Maps the display names used in specs to match what we use in
# the Reference Library so filtering works correctly
# ─────────────────────────────────────────────────────────────
SUBJECT_ALIASES = {
    "Art and Design": ["Art & Design", "Art", "Photography", "Textiles", "3D Design"],
    "Physical Education": ["PE"],
    "Design and Technology": ["DT", "D&T"],
    "Modern Foreign Languages": ["MFL", "French", "Spanish", "German"],
    "Religious Studies": ["RS", "RE"],
    "Mathematics": ["Maths"],
    "Computing": ["Computer Science"],
    "Business Studies": ["Business"],
    "PSHE & Citizenship": ["PSHE", "Citizenship"],
    "Information Technology": ["IT", "ICT"],
}


# ─────────────────────────────────────────────────────────────
# DOWNLOAD ENGINE
# ─────────────────────────────────────────────────────────────

def _download_file(url, dest_path, retries=3):
    """Download a file from URL to dest_path with retries."""
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        print(f"  ⏭️  Already exists: {dest_path.name}")
        return True

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*",
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
                if len(data) < 1000:
                    print(f"  ⚠️  File too small ({len(data)} bytes), may be an error page: {dest_path.name}")
                    return False
                dest_path.write_bytes(data)
                size_kb = len(data) / 1024
                print(f"  ✅ {dest_path.name} ({size_kb:.0f} KB)")
                return True
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt < retries - 1:
                print(f"  ⚠️  Retry {attempt + 1}/{retries} for {dest_path.name}: {e}")
                time.sleep(2)
            else:
                print(f"  ❌ Failed to download {dest_path.name}: {e}")
                return False


def download_nc(subject_filter=None):
    """Download National Curriculum documents from GOV.UK."""
    print("\n📚 Downloading National Curriculum documents...")
    downloaded = 0
    failed = 0

    for subject, info in sorted(NC_DOCUMENTS.items()):
        if subject_filter and subject.lower() != subject_filter.lower():
            continue

        for f in info["files"]:
            dest = NC_DIR / f["filename"]
            ks_label = ", ".join(f["key_stages"])
            print(f"\n  {subject} ({ks_label})")
            if _download_file(f["url"], dest):
                downloaded += 1
            else:
                failed += 1

    print(f"\n📚 NC: {downloaded} downloaded, {failed} failed")
    return downloaded, failed


def download_specs(subject_filter=None):
    """Download exam board specifications."""
    print("\n📋 Downloading exam board specifications...")
    downloaded = 0
    failed = 0

    for subject, boards in sorted(EXAM_SPECS.items()):
        if subject_filter and subject.lower() != subject_filter.lower():
            continue

        for board, levels in sorted(boards.items()):
            for level, info in sorted(levels.items()):
                board_dir = SPECS_DIR / board.lower()
                board_dir.mkdir(parents=True, exist_ok=True)
                dest = board_dir / info["filename"]
                print(f"\n  {info['name']} ({board} {level})")
                if _download_file(info["url"], dest):
                    downloaded += 1
                else:
                    failed += 1
                time.sleep(0.5)  # Be polite to servers

    print(f"\n📋 Specs: {downloaded} downloaded, {failed} failed")
    return downloaded, failed


def import_to_library():
    """Import all downloaded NC and spec files into Reference Library."""
    from reference_library import save_document, list_documents

    imported = 0
    errors = 0

    # Import National Curriculum docs
    print("\n📚 Importing National Curriculum documents...")
    for subject, info in sorted(NC_DOCUMENTS.items()):
        for f in info["files"]:
            path = NC_DIR / f["filename"]
            if not path.exists():
                continue

            for ks in f["key_stages"]:
                title = f"National Curriculum: {subject} ({ks})"
                try:
                    save_document(
                        file_path=str(path),
                        category="national_curriculum",
                        title=title,
                        subject=subject,
                        key_stage=ks,
                        description=f"DfE statutory programme of study for {subject} at {ks}",
                    )
                    imported += 1
                    print(f"  ✅ {title}")
                except Exception as e:
                    errors += 1

    # Import exam specs
    print("\n📋 Importing exam specifications...")
    for subject, boards in sorted(EXAM_SPECS.items()):
        for board, levels in sorted(boards.items()):
            for level, info in sorted(levels.items()):
                board_dir = SPECS_DIR / board.lower()
                path = board_dir / info["filename"]
                if not path.exists():
                    continue

                # Determine key stage from level
                if "GCSE" in level:
                    ks = "KS4"
                elif "A Level" in level or "A level" in level:
                    ks = "KS5"
                else:
                    ks = "KS4"

                title = info["name"]
                try:
                    save_document(
                        file_path=str(path),
                        category="ks4_spec",
                        title=title,
                        subject=subject,
                        key_stage=ks,
                        exam_board=board,
                        description=f"{board} {level} specification for {subject}",
                    )
                    imported += 1
                    print(f"  ✅ {title}")
                except Exception as e:
                    errors += 1

    total_docs = len(list_documents())
    print(f"\n✅ Imported {imported} documents ({errors} errors/duplicates)")
    print(f"📚 Reference Library now has {total_docs} documents total")
    return imported, errors


def list_all():
    """List all documents that would be downloaded."""
    print("\n📚 NATIONAL CURRICULUM (GOV.UK)")
    print("-" * 60)
    nc_count = 0
    for subject, info in sorted(NC_DOCUMENTS.items()):
        for f in info["files"]:
            ks = ", ".join(f["key_stages"])
            exists = "✅" if (NC_DIR / f["filename"]).exists() else "  "
            print(f"  {exists} {subject} ({ks}) — {f['filename']}")
            nc_count += 1

    print(f"\n📋 EXAM SPECIFICATIONS")
    print("-" * 60)
    total = 0
    for subject, boards in sorted(EXAM_SPECS.items()):
        print(f"\n  {subject}:")
        for board, levels in sorted(boards.items()):
            for level, info in sorted(levels.items()):
                board_dir = SPECS_DIR / board.lower()
                exists = "✅" if (board_dir / info["filename"]).exists() else "  "
                print(f"    {exists} {board} {level}: {info['name']}")
                total += 1

    print(f"\n📊 Total: {nc_count} NC documents + {total} exam specs = {nc_count + total} files")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download NC and exam specs for UK curriculum")
    parser.add_argument("--nc-only", action="store_true", help="Only download National Curriculum")
    parser.add_argument("--specs-only", action="store_true", help="Only download exam specifications")
    parser.add_argument("--subject", "-s", help="Filter by subject name")
    parser.add_argument("--import", "-i", dest="do_import", action="store_true", help="Import downloaded files into Reference Library")
    parser.add_argument("--list", "-l", action="store_true", help="List what would be downloaded")
    parser.add_argument("--all", "-a", action="store_true", help="Download everything")
    args = parser.parse_args()

    if args.list:
        list_all()
    elif args.do_import:
        import_to_library()
    elif args.nc_only:
        download_nc(args.subject)
    elif args.specs_only:
        download_specs(args.subject)
    elif args.all or not args.subject:
        download_nc(args.subject)
        download_specs(args.subject)
    else:
        download_nc(args.subject)
        download_specs(args.subject)
