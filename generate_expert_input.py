#!/usr/bin/env python3
"""
Expert Input File Generator

Generates curriculum knowledge-base markdown files for any UK school subject,
following the same structure as the original handoff files.

Usage:
    python generate_expert_input.py                    # Generate ALL pending subjects
    python generate_expert_input.py --subject art      # Generate one subject
    python generate_expert_input.py --list              # List available subjects
    python generate_expert_input.py --import            # Import generated files into Reference Library

To add a new subject:
    1. Add an entry to SUBJECTS dict below
    2. Run: python generate_expert_input.py --subject your_subject_key
    3. Run: python generate_expert_input.py --import
"""

import argparse
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# ─────────────────────────────────────────────────────────────
# OUTPUT DIRECTORY
# ─────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "data" / "expert-input-generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# SUBJECT DEFINITIONS
#
# To add a new subject, copy an existing block and fill in:
#   - name: display name
#   - folder: subfolder name under OUTPUT_DIR
#   - thinkers: list of {"name": ..., "focus": ...}
#   - categories: list of {"folder": ..., "label": ..., "files": [...]}
#     Each file is {"name": "filename.md", "title": "Heading for the file"}
# ─────────────────────────────────────────────────────────────
SUBJECTS = {

    "computing": {
        "name": "Computing",
        "folder": "computing-curriculum",
        "thinkers": [
            {"name": "Mark Dorling", "focus": "Barefoot Computing, primary computing, computational thinking progression"},
            {"name": "Simon Peyton Jones", "focus": "Computing At School (CAS), National Curriculum for Computing, functional programming"},
            {"name": "Phil Bagge", "focus": "primary computing pedagogy, Code-It, computational thinking activities"},
            {"name": "Miles Berry", "focus": "Roehampton, computing education research, Scratch, curriculum design"},
            {"name": "Sue Sentance", "focus": "Raspberry Pi Foundation, computing pedagogy research, PRIMM framework, King's College London"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Computing National Curriculum Overview"},
                {"name": "ks1.md", "title": "Computing at Key Stage 1"},
                {"name": "ks2.md", "title": "Computing at Key Stage 2"},
                {"name": "ks3.md", "title": "Computing at Key Stage 3"},
                {"name": "ks4.md", "title": "Computing at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Computing at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "computational_thinking.md", "title": "Computational Thinking"},
                {"name": "programming_concepts.md", "title": "Programming Concepts and Progression"},
                {"name": "algorithms.md", "title": "Algorithms and Data Structures"},
                {"name": "data_representation.md", "title": "Data Representation and Binary"},
                {"name": "networks_and_internet.md", "title": "Networks and the Internet"},
                {"name": "cybersecurity.md", "title": "Cybersecurity and E-Safety"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "primm.md", "title": "The PRIMM Framework (Predict-Run-Investigate-Modify-Make)"},
                {"name": "unplugged_activities.md", "title": "Unplugged Computing Activities"},
                {"name": "pair_programming.md", "title": "Pair Programming and Collaborative Coding"},
                {"name": "debugging_strategies.md", "title": "Teaching Debugging Strategies"},
                {"name": "differentiation.md", "title": "Differentiation in Computing"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "formative_assessment.md", "title": "Formative Assessment in Computing"},
                {"name": "gcse_specifications.md", "title": "GCSE Computer Science Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Computer Science Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "cas.md", "title": "Computing At School (CAS)"},
                {"name": "raspberry_pi.md", "title": "Raspberry Pi Foundation"},
                {"name": "ncce.md", "title": "National Centre for Computing Education"},
                {"name": "ofsted_computing.md", "title": "Ofsted and Computing"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Computing Across Key Stages"},
                {"name": "progression.md", "title": "Progression in Programming"},
                {"name": "digital_literacy.md", "title": "Digital Literacy Across the Curriculum"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "gender_gap.md", "title": "Addressing the Gender Gap in Computing"},
                {"name": "send_in_computing.md", "title": "SEND in Computing"},
                {"name": "disadvantaged_pupils.md", "title": "Disadvantaged Pupils and Digital Access"},
            ]},
        ],
    },

    "art": {
        "name": "Art & Design",
        "folder": "art-curriculum",
        "thinkers": [
            {"name": "Eileen Adams", "focus": "built environment education, design education, drawing, Power Drawing"},
            {"name": "John Steers", "focus": "NSEAD, international art education, creativity in schools, curriculum policy"},
            {"name": "Rachel Mason", "focus": "multicultural art education, community arts, international perspectives"},
            {"name": "Leslie Cunliffe", "focus": "aesthetic understanding, visual literacy, art appreciation pedagogy"},
            {"name": "Jeff Adams", "focus": "documentary methods in art education, contemporary art, visual culture pedagogy"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Art & Design National Curriculum Overview"},
                {"name": "eyfs.md", "title": "Art & Design in EYFS"},
                {"name": "ks1.md", "title": "Art & Design at Key Stage 1"},
                {"name": "ks2.md", "title": "Art & Design at Key Stage 2"},
                {"name": "ks3.md", "title": "Art & Design at Key Stage 3"},
                {"name": "ks4.md", "title": "Art & Design at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Art & Design at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "drawing.md", "title": "Drawing Skills and Progression"},
                {"name": "painting.md", "title": "Painting Techniques and Media"},
                {"name": "printmaking.md", "title": "Printmaking Across Key Stages"},
                {"name": "sculpture.md", "title": "Sculpture and 3D Work"},
                {"name": "digital_art.md", "title": "Digital Art and New Media"},
                {"name": "art_history.md", "title": "Art History and Contextual Studies"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "sketchbook_practice.md", "title": "Sketchbook Practice and Process"},
                {"name": "critical_studies.md", "title": "Critical and Contextual Studies"},
                {"name": "creative_process.md", "title": "Teaching the Creative Process"},
                {"name": "assessment_art.md", "title": "Assessment in Art & Design"},
                {"name": "artist_study.md", "title": "Studying Artists, Craftspeople and Designers"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Art & Design Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Art & Design Specifications"},
                {"name": "formative_assessment.md", "title": "Formative Assessment in Art"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "nsead.md", "title": "National Society for Education in Art and Design (NSEAD)"},
                {"name": "accessart.md", "title": "AccessArt"},
                {"name": "ofsted_art.md", "title": "Ofsted and Art Education"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Art Across Key Stages"},
                {"name": "progression_in_skills.md", "title": "Progression in Art Skills"},
                {"name": "cultural_capital.md", "title": "Cultural Capital in Art Education"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "diverse_artists.md", "title": "Diversity in Artist Selection"},
                {"name": "send_in_art.md", "title": "SEND in Art & Design"},
                {"name": "adaptive_teaching.md", "title": "Adaptive Teaching in Art"},
            ]},
        ],
    },

    "music": {
        "name": "Music",
        "folder": "music-curriculum",
        "thinkers": [
            {"name": "Martin Fautley", "focus": "assessment in music, musical futures, BCU, inclusive music education"},
            {"name": "Lucy Green", "focus": "informal learning, Musical Futures, popular music pedagogy, UCL IOE"},
            {"name": "Keith Swanwick", "focus": "CLASP model, musical knowledge, musical development, UCL IOE"},
            {"name": "Zoltan Kodaly", "focus": "singing-based approach, solfa, sequential music education, folk music"},
            {"name": "Gary Spruce", "focus": "Open University, music curriculum policy, inclusion, cultural identity"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Music National Curriculum Overview"},
                {"name": "eyfs.md", "title": "Music in EYFS"},
                {"name": "ks1.md", "title": "Music at Key Stage 1"},
                {"name": "ks2.md", "title": "Music at Key Stage 2"},
                {"name": "ks3.md", "title": "Music at Key Stage 3"},
                {"name": "ks4.md", "title": "Music at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Music at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "performing.md", "title": "Performing: Singing and Instrumental"},
                {"name": "composing.md", "title": "Composing Across Key Stages"},
                {"name": "listening_appraising.md", "title": "Listening and Appraising"},
                {"name": "music_theory.md", "title": "Music Theory and Notation"},
                {"name": "music_technology.md", "title": "Music Technology"},
                {"name": "world_music.md", "title": "World Music and Cultural Diversity"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "whole_class_ensemble.md", "title": "Whole Class Ensemble Teaching"},
                {"name": "musical_futures.md", "title": "Musical Futures and Informal Learning"},
                {"name": "kodaly_approach.md", "title": "Kodaly and Singing-Based Approaches"},
                {"name": "differentiation.md", "title": "Differentiation in Music"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "formative_assessment.md", "title": "Formative Assessment in Music"},
                {"name": "gcse_specifications.md", "title": "GCSE Music Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Music Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "music_hubs.md", "title": "Music Hubs and Music Education Partnerships"},
                {"name": "isr.md", "title": "ISM and Music Education Bodies"},
                {"name": "ofsted_music.md", "title": "Ofsted and Music Education"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Music Across Key Stages"},
                {"name": "progression.md", "title": "Progression in Musical Skills"},
                {"name": "model_music_curriculum.md", "title": "The Model Music Curriculum"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "send_in_music.md", "title": "SEND in Music"},
                {"name": "disadvantaged_pupils.md", "title": "Disadvantaged Pupils and Music Access"},
                {"name": "diversity_in_repertoire.md", "title": "Diversity in Musical Repertoire"},
            ]},
        ],
    },

    "pe": {
        "name": "Physical Education",
        "folder": "pe-curriculum",
        "thinkers": [
            {"name": "Margaret Whitehead", "focus": "physical literacy, holistic PE, motivation, embodiment"},
            {"name": "David Kirk", "focus": "models-based practice, situated learning, PE futures, Strathclyde"},
            {"name": "Dawn Penney", "focus": "curriculum policy, equity in PE, pedagogy, Edith Cowan University"},
            {"name": "Len Almond", "focus": "Teaching Games for Understanding (TGfU), health-related PE, Loughborough"},
            {"name": "Susan Capel", "focus": "PE teacher education, Brunel, learning to teach PE, mentoring"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "PE National Curriculum Overview"},
                {"name": "eyfs.md", "title": "Physical Development in EYFS"},
                {"name": "ks1.md", "title": "PE at Key Stage 1"},
                {"name": "ks2.md", "title": "PE at Key Stage 2"},
                {"name": "ks3.md", "title": "PE at Key Stage 3"},
                {"name": "ks4.md", "title": "PE at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "PE at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "games.md", "title": "Games and Sport"},
                {"name": "gymnastics.md", "title": "Gymnastics"},
                {"name": "dance.md", "title": "Dance in PE"},
                {"name": "athletics.md", "title": "Athletics"},
                {"name": "swimming.md", "title": "Swimming and Water Safety"},
                {"name": "outdoor_adventurous.md", "title": "Outdoor and Adventurous Activities"},
                {"name": "anatomy_physiology.md", "title": "Anatomy and Physiology for GCSE/A Level"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "tgfu.md", "title": "Teaching Games for Understanding (TGfU)"},
                {"name": "sport_education.md", "title": "Sport Education Model"},
                {"name": "cooperative_learning.md", "title": "Cooperative Learning in PE"},
                {"name": "physical_literacy.md", "title": "Teaching for Physical Literacy"},
                {"name": "health_related.md", "title": "Health-Related PE"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "formative_assessment.md", "title": "Formative Assessment in PE"},
                {"name": "gcse_specifications.md", "title": "GCSE PE Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level PE Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "afpe.md", "title": "Association for Physical Education (afPE)"},
                {"name": "youth_sport_trust.md", "title": "Youth Sport Trust"},
                {"name": "ofsted_pe.md", "title": "Ofsted and PE"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing PE Across Key Stages"},
                {"name": "progression.md", "title": "Progression in PE Skills and Knowledge"},
                {"name": "extra_curricular.md", "title": "Extra-Curricular Sport and PE"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "send_in_pe.md", "title": "SEND in PE"},
                {"name": "gender_equity.md", "title": "Gender Equity in PE"},
                {"name": "adaptive_pe.md", "title": "Adaptive PE and Inclusive Practice"},
            ]},
        ],
    },

    "drama": {
        "name": "Drama",
        "folder": "drama-curriculum",
        "thinkers": [
            {"name": "Dorothy Heathcote", "focus": "mantle of the expert, drama for learning, process drama"},
            {"name": "Jonothan Neelands", "focus": "conventions approach, drama structures, ensemble, Warwick"},
            {"name": "Cecily O'Neill", "focus": "process drama, pre-text, structuring drama, Ohio State"},
            {"name": "Gavin Bolton", "focus": "drama in education, understanding and acting, Durham"},
            {"name": "Andy Kempe", "focus": "drama education research, practical approaches, Reading"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Drama in the National Curriculum Overview"},
                {"name": "eyfs.md", "title": "Drama in EYFS"},
                {"name": "ks1_ks2.md", "title": "Drama at Key Stages 1 and 2"},
                {"name": "ks3.md", "title": "Drama at Key Stage 3"},
                {"name": "ks4.md", "title": "Drama at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Drama at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "devising.md", "title": "Devising Drama"},
                {"name": "scripted_performance.md", "title": "Scripted Performance"},
                {"name": "practitioners.md", "title": "Key Practitioners (Brecht, Stanislavski, Artaud, etc.)"},
                {"name": "technical_theatre.md", "title": "Technical Theatre (Lighting, Sound, Set)"},
                {"name": "physical_theatre.md", "title": "Physical Theatre and Movement"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "process_drama.md", "title": "Process Drama"},
                {"name": "mantle_of_expert.md", "title": "Mantle of the Expert"},
                {"name": "conventions.md", "title": "Drama Conventions and Strategies"},
                {"name": "rehearsal_techniques.md", "title": "Rehearsal Techniques"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "formative_assessment.md", "title": "Formative Assessment in Drama"},
                {"name": "gcse_specifications.md", "title": "GCSE Drama Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Drama and Theatre Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "national_drama.md", "title": "National Drama"},
                {"name": "ofsted_drama.md", "title": "Ofsted and Drama Education"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Drama Across Key Stages"},
                {"name": "progression.md", "title": "Progression in Drama Skills"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "send_in_drama.md", "title": "SEND in Drama"},
                {"name": "cultural_diversity.md", "title": "Cultural Diversity in Drama"},
            ]},
        ],
    },

    "dt": {
        "name": "Design & Technology",
        "folder": "dt-curriculum",
        "thinkers": [
            {"name": "David Barlex", "focus": "Nuffield Design & Technology, curriculum design, design without make, Young Foresight"},
            {"name": "Richard Kimbell", "focus": "Goldsmiths, assessment of design capability, e-scape, APU"},
            {"name": "Kay Stables", "focus": "design cognition, assessment, primary D&T, Goldsmiths"},
            {"name": "Stephanie Atkinson", "focus": "Sunderland, food technology, textiles technology, health and safety"},
            {"name": "Matt McLain", "focus": "Edge Hill, maker pedagogy, D&T curriculum, teacher education"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "D&T National Curriculum Overview"},
                {"name": "eyfs.md", "title": "D&T in EYFS"},
                {"name": "ks1.md", "title": "D&T at Key Stage 1"},
                {"name": "ks2.md", "title": "D&T at Key Stage 2"},
                {"name": "ks3.md", "title": "D&T at Key Stage 3"},
                {"name": "ks4.md", "title": "D&T at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "D&T at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "materials_and_components.md", "title": "Materials and Components"},
                {"name": "structures_mechanisms.md", "title": "Structures and Mechanisms"},
                {"name": "electronics_systems.md", "title": "Electronics and Systems"},
                {"name": "food_and_nutrition.md", "title": "Food and Nutrition"},
                {"name": "design_process.md", "title": "The Design Process"},
                {"name": "cad_cam.md", "title": "CAD/CAM and Digital Manufacturing"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "iterative_design.md", "title": "Iterative Design in the Classroom"},
                {"name": "practical_skills.md", "title": "Teaching Practical Skills Safely"},
                {"name": "design_thinking.md", "title": "Design Thinking Approaches"},
                {"name": "nutrition_education.md", "title": "Nutrition Education Pedagogy"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "formative_assessment.md", "title": "Formative Assessment in D&T"},
                {"name": "gcse_specifications.md", "title": "GCSE D&T Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level D&T Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "data.md", "title": "Design and Technology Association (DATA)"},
                {"name": "ofsted_dt.md", "title": "Ofsted and D&T"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing D&T Across Key Stages"},
                {"name": "progression.md", "title": "Progression in Design and Making"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "send_in_dt.md", "title": "SEND in D&T"},
                {"name": "gender_equity.md", "title": "Gender Equity in D&T"},
            ]},
        ],
    },

    "pshe": {
        "name": "PSHE & Citizenship",
        "folder": "pshe-curriculum",
        "thinkers": [
            {"name": "Jenny Mosley", "focus": "circle time, Quality Circle Time, positive relationships, self-esteem"},
            {"name": "Bernard Crick", "focus": "citizenship education, Crick Report 1998, political literacy, active citizenship"},
            {"name": "Nick Boddington", "focus": "PSHE Association, drug and alcohol education, curriculum development"},
            {"name": "Lee Jerome", "focus": "Middlesex University, citizenship pedagogy, human rights education"},
            {"name": "Jonathan Charlesworth", "focus": "PSHE Association CEO, statutory RSE, mental health education"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "PSHE and Citizenship Overview"},
                {"name": "eyfs.md", "title": "PSED in EYFS"},
                {"name": "ks1.md", "title": "PSHE at Key Stage 1"},
                {"name": "ks2.md", "title": "PSHE at Key Stage 2"},
                {"name": "ks3.md", "title": "PSHE at Key Stage 3"},
                {"name": "ks4.md", "title": "PSHE at Key Stage 4"},
                {"name": "statutory_rse.md", "title": "Statutory RSE and Health Education"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "health_wellbeing.md", "title": "Health and Wellbeing"},
                {"name": "relationships.md", "title": "Relationships Education"},
                {"name": "living_in_wider_world.md", "title": "Living in the Wider World"},
                {"name": "citizenship.md", "title": "Citizenship: Democracy and Law"},
                {"name": "financial_education.md", "title": "Financial Education"},
                {"name": "mental_health.md", "title": "Mental Health Education"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "distancing_techniques.md", "title": "Distancing Techniques in PSHE"},
                {"name": "ground_rules.md", "title": "Ground Rules and Safe Learning"},
                {"name": "active_citizenship.md", "title": "Teaching Active Citizenship"},
                {"name": "sensitive_topics.md", "title": "Handling Sensitive and Controversial Topics"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "formative_assessment.md", "title": "Formative Assessment in PSHE"},
                {"name": "gcse_citizenship.md", "title": "GCSE Citizenship Studies Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "pshe_association.md", "title": "PSHE Association"},
                {"name": "ofsted_pshe.md", "title": "Ofsted and PSHE"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "spiral_curriculum.md", "title": "Spiral Curriculum in PSHE"},
                {"name": "progression.md", "title": "Progression in PSHE"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "send_in_pshe.md", "title": "SEND in PSHE"},
                {"name": "lgbtq_inclusion.md", "title": "LGBTQ+ Inclusion in RSE"},
            ]},
        ],
    },

    "business": {
        "name": "Business Studies",
        "folder": "business-curriculum",
        "thinkers": [
            {"name": "Ian Marcousé", "focus": "business education author, A Level Business, Hodder textbooks"},
            {"name": "Peter Stimpson", "focus": "Cambridge IGCSE and A Level Business, international business education"},
            {"name": "Mark Surridge", "focus": "Tutor2u, business education resources, exam technique, A Level"},
            {"name": "Jim Riley", "focus": "Tutor2u founder, economics and business education, digital resources"},
            {"name": "Nancy Wall", "focus": "Enterprise education, Nuffield economics, critical thinking in business"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Business Studies Curriculum Overview"},
                {"name": "ks4.md", "title": "Business Studies at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Business Studies at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "enterprise.md", "title": "Enterprise and Entrepreneurship"},
                {"name": "marketing.md", "title": "Marketing"},
                {"name": "finance.md", "title": "Business Finance and Accounting"},
                {"name": "operations.md", "title": "Operations Management"},
                {"name": "human_resources.md", "title": "Human Resource Management"},
                {"name": "external_influences.md", "title": "External Influences on Business"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "case_studies.md", "title": "Using Case Studies in Business"},
                {"name": "enterprise_activities.md", "title": "Enterprise Activities in School"},
                {"name": "quantitative_skills.md", "title": "Teaching Quantitative Skills"},
                {"name": "exam_technique.md", "title": "Exam Technique and Extended Writing"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Business Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Business Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "ebea.md", "title": "Economics, Business and Enterprise Association (EBEA)"},
                {"name": "tutor2u.md", "title": "Tutor2u and Digital Resources"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Business Studies"},
                {"name": "progression.md", "title": "Progression from GCSE to A Level"},
            ]},
            {"folder": "08_inclusion_equity", "label": "Inclusion and Equity", "files": [
                {"name": "send_in_business.md", "title": "SEND in Business Studies"},
                {"name": "disadvantaged_pupils.md", "title": "Disadvantaged Pupils and Business Education"},
            ]},
        ],
    },

    "textiles": {
        "name": "Textiles",
        "folder": "textiles-curriculum",
        "thinkers": [
            {"name": "Stephanie Atkinson", "focus": "Sunderland, textiles education research, health and safety, D&T pedagogy"},
            {"name": "Kay Stables", "focus": "design cognition, assessment, creativity in textiles, Goldsmiths"},
            {"name": "Alice Kettle", "focus": "Manchester School of Art, contemporary textiles, stitch, large-scale work"},
            {"name": "Cas Holmes", "focus": "mixed media textiles, sustainability, found materials, UCA"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Textiles in the National Curriculum"},
                {"name": "ks1_ks2.md", "title": "Textiles at Key Stages 1 and 2"},
                {"name": "ks3.md", "title": "Textiles at Key Stage 3"},
                {"name": "ks4.md", "title": "Textiles at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Textiles at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "fibres_and_fabrics.md", "title": "Fibres and Fabrics"},
                {"name": "surface_decoration.md", "title": "Surface Decoration Techniques"},
                {"name": "construction_techniques.md", "title": "Construction Techniques"},
                {"name": "pattern_and_design.md", "title": "Pattern Cutting and Design"},
                {"name": "smart_materials.md", "title": "Smart and Modern Materials in Textiles"},
                {"name": "sustainability.md", "title": "Sustainability in Textiles"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "practical_skills.md", "title": "Teaching Practical Textiles Skills"},
                {"name": "design_process.md", "title": "The Design Process in Textiles"},
                {"name": "cultural_textiles.md", "title": "Cultural Contexts in Textiles"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Textiles Design Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Textiles Design Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "textiles_organisations.md", "title": "Key Textiles Education Organisations"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Textiles Across Key Stages"},
                {"name": "progression.md", "title": "Progression in Textiles Skills"},
            ]},
        ],
    },

    "it": {
        "name": "Information Technology",
        "folder": "it-curriculum",
        "thinkers": [
            {"name": "Miles Berry", "focus": "Roehampton, digital literacy, IT curriculum, computing education"},
            {"name": "Bob Harrison", "focus": "education technology, Toshiba Chair in Ed Tech, digital strategy"},
            {"name": "Mark Anderson", "focus": "ICT Evangelist, digital learning, ed-tech implementation"},
            {"name": "Neil Selwyn", "focus": "Monash, critical ed-tech, digital inequalities, technology and education policy"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "IT in the National Curriculum Overview"},
                {"name": "ks3.md", "title": "IT at Key Stage 3"},
                {"name": "ks4.md", "title": "IT at Key Stage 4 (Cambridge Nationals, BTEC, etc.)"},
                {"name": "ks5.md", "title": "IT at Key Stage 5 (BTEC, Cambridge Technicals)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "spreadsheets_databases.md", "title": "Spreadsheets and Databases"},
                {"name": "web_development.md", "title": "Web Development"},
                {"name": "digital_media.md", "title": "Digital Media and Graphics"},
                {"name": "project_management.md", "title": "IT Project Management"},
                {"name": "data_analytics.md", "title": "Data Analytics and Visualisation"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "practical_projects.md", "title": "Project-Based Learning in IT"},
                {"name": "digital_literacy.md", "title": "Teaching Digital Literacy"},
                {"name": "industry_links.md", "title": "Industry Links and Employability"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "vocational_qualifications.md", "title": "Vocational IT Qualifications (BTEC, Cambridge Nationals)"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "bcs.md", "title": "BCS, The Chartered Institute for IT"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing IT Across Key Stages"},
                {"name": "progression.md", "title": "Progression from IT to Computing and Vice Versa"},
            ]},
        ],
    },

    "photography": {
        "name": "Photography",
        "folder": "photography-curriculum",
        "thinkers": [
            {"name": "John Ingledew", "focus": "photography education author, creativity in photography, Westminster"},
            {"name": "Charlotte Cotton", "focus": "The Photograph as Contemporary Art, curation, ICP"},
            {"name": "David Bate", "focus": "photography theory, genres, Westminster, research-informed pedagogy"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Photography in the Curriculum Overview"},
                {"name": "ks3.md", "title": "Photography at Key Stage 3"},
                {"name": "ks4.md", "title": "Photography at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Photography at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "camera_techniques.md", "title": "Camera Techniques and Exposure"},
                {"name": "composition.md", "title": "Composition and Visual Language"},
                {"name": "digital_editing.md", "title": "Digital Editing and Post-Production"},
                {"name": "genres.md", "title": "Photographic Genres (Portrait, Landscape, Documentary, etc.)"},
                {"name": "history_of_photography.md", "title": "History of Photography"},
                {"name": "lighting.md", "title": "Lighting Techniques"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "visual_literacy.md", "title": "Teaching Visual Literacy Through Photography"},
                {"name": "photo_projects.md", "title": "Structuring Photography Projects"},
                {"name": "critical_analysis.md", "title": "Teaching Critical Analysis of Photographs"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Photography Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Photography Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "photography_organisations.md", "title": "Key Photography Education Organisations"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Photography Projects"},
                {"name": "progression.md", "title": "Progression in Photography Skills"},
            ]},
        ],
    },

    "3d_design": {
        "name": "3D Design",
        "folder": "3d-design-curriculum",
        "thinkers": [
            {"name": "Richard Kimbell", "focus": "Goldsmiths, design capability, assessment, APU, e-scape"},
            {"name": "David Barlex", "focus": "Nuffield D&T, design without make, 3D design curriculum"},
            {"name": "Nigel Cross", "focus": "design thinking, design cognition, Open University, Designerly Ways of Knowing"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "3D Design in the Curriculum Overview"},
                {"name": "ks3.md", "title": "3D Design at Key Stage 3"},
                {"name": "ks4.md", "title": "3D Design at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "3D Design at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "materials.md", "title": "Materials for 3D Design (Wood, Metal, Ceramics, Plastics)"},
                {"name": "form_and_function.md", "title": "Form, Function and Aesthetics"},
                {"name": "product_design.md", "title": "Product Design Principles"},
                {"name": "architectural_design.md", "title": "Architectural and Environmental Design"},
                {"name": "cad_3d_printing.md", "title": "CAD and 3D Printing"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "design_process.md", "title": "Teaching the 3D Design Process"},
                {"name": "workshop_skills.md", "title": "Workshop Skills and Safety"},
                {"name": "model_making.md", "title": "Model Making and Prototyping"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE 3D Design Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level 3D Design Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "design_organisations.md", "title": "Key 3D Design Education Organisations"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing 3D Design Across Key Stages"},
                {"name": "progression.md", "title": "Progression in 3D Design Skills"},
            ]},
        ],
    },

    "statistics": {
        "name": "Statistics",
        "folder": "statistics-curriculum",
        "thinkers": [
            {"name": "Anne Watson", "focus": "Oxford, mathematical thinking, variation theory, task design"},
            {"name": "Malcolm Swan", "focus": "Shell Centre, formative assessment, collaborative tasks, Nottingham"},
            {"name": "Adrian Sheratt", "focus": "statistics education, RSS, data literacy, applied statistics teaching"},
            {"name": "David Spiegelhalter", "focus": "Cambridge, public understanding of risk, data visualisation, statistics communication"},
        ],
        "categories": [
            {"folder": "01_national_curriculum", "label": "National Curriculum", "files": [
                {"name": "overview.md", "title": "Statistics in the Curriculum Overview"},
                {"name": "ks3_ks4_within_maths.md", "title": "Statistics Within KS3/KS4 Mathematics"},
                {"name": "ks4.md", "title": "GCSE Statistics"},
                {"name": "ks5.md", "title": "A Level Statistics (Within Mathematics and Further Maths)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "data_collection.md", "title": "Data Collection and Sampling"},
                {"name": "data_presentation.md", "title": "Data Presentation and Interpretation"},
                {"name": "probability.md", "title": "Probability"},
                {"name": "statistical_measures.md", "title": "Statistical Measures (Averages, Spread, Correlation)"},
                {"name": "hypothesis_testing.md", "title": "Hypothesis Testing (A Level)"},
                {"name": "distributions.md", "title": "Statistical Distributions (A Level)"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "real_data.md", "title": "Using Real Data in Teaching Statistics"},
                {"name": "statistical_literacy.md", "title": "Teaching Statistical Literacy"},
                {"name": "technology_in_stats.md", "title": "Technology in Statistics Teaching"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_statistics.md", "title": "GCSE Statistics Specifications"},
                {"name": "a_level_statistics.md", "title": "A Level Statistics Components"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "rss.md", "title": "Royal Statistical Society and Education"},
                {"name": "census_at_school.md", "title": "CensusAtSchool and Data Resources"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Statistics Across Key Stages"},
                {"name": "progression.md", "title": "Progression in Statistical Thinking"},
            ]},
        ],
    },

    "sociology": {
        "name": "Sociology",
        "folder": "sociology-curriculum",
        "thinkers": [
            {"name": "Ken Browne", "focus": "introductory sociology, GCSE/A Level textbooks, accessible pedagogy"},
            {"name": "Steve Chapman", "focus": "A Level sociology, social stratification, family, Collins textbooks"},
            {"name": "Mike Haralambos", "focus": "Haralambos & Holborn, comprehensive A Level textbook, sociology education"},
            {"name": "Heidi Safia Mirza", "focus": "race, gender and education, Black British feminism, UCL IOE"},
            {"name": "Diane Reay", "focus": "Cambridge, social class and education, Miseducation, cultural capital"},
        ],
        "categories": [
            {"folder": "01_curriculum_overview", "label": "Curriculum Overview", "files": [
                {"name": "overview.md", "title": "Sociology Curriculum Overview (A Level)"},
                {"name": "ks4.md", "title": "Sociology at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Sociology at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "socialisation_culture.md", "title": "Socialisation, Culture and Identity"},
                {"name": "family.md", "title": "Families and Households"},
                {"name": "education.md", "title": "Education"},
                {"name": "crime_deviance.md", "title": "Crime and Deviance"},
                {"name": "stratification.md", "title": "Social Stratification and Inequality"},
                {"name": "beliefs.md", "title": "Beliefs in Society"},
                {"name": "research_methods.md", "title": "Research Methods"},
                {"name": "media.md", "title": "The Media"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "sociological_imagination.md", "title": "Teaching the Sociological Imagination"},
                {"name": "applying_theory.md", "title": "Applying Sociological Theory"},
                {"name": "essay_skills.md", "title": "Extended Writing and Essay Skills"},
                {"name": "using_data.md", "title": "Using Data and Research in Sociology"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Sociology Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Sociology Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "bsa.md", "title": "British Sociological Association and Education"},
                {"name": "tutor2u_sociology.md", "title": "Tutor2u Sociology Resources"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Sociology Topics"},
                {"name": "progression.md", "title": "Progression from GCSE to A Level Sociology"},
            ]},
        ],
    },

    "psychology": {
        "name": "Psychology",
        "folder": "psychology-curriculum",
        "thinkers": [
            {"name": "Cara Flanagan", "focus": "A Level psychology textbooks, AQA, student-centred resources"},
            {"name": "Philip Banyard", "focus": "Nottingham Trent, applied psychology, ethics, A Level pedagogy"},
            {"name": "Mark Billingham", "focus": "psychology teaching, AQA development, exam board work"},
            {"name": "Mike Cardwell", "focus": "psychology education, A Level textbooks, Hodder resources"},
        ],
        "categories": [
            {"folder": "01_curriculum_overview", "label": "Curriculum Overview", "files": [
                {"name": "overview.md", "title": "Psychology Curriculum Overview (A Level)"},
                {"name": "ks4.md", "title": "Psychology at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Psychology at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "social_influence.md", "title": "Social Influence"},
                {"name": "memory.md", "title": "Memory"},
                {"name": "attachment.md", "title": "Attachment"},
                {"name": "approaches.md", "title": "Approaches in Psychology"},
                {"name": "psychopathology.md", "title": "Psychopathology"},
                {"name": "biopsychology.md", "title": "Biopsychology"},
                {"name": "research_methods.md", "title": "Research Methods"},
                {"name": "issues_debates.md", "title": "Issues and Debates in Psychology"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "teaching_research_methods.md", "title": "Teaching Research Methods in Psychology"},
                {"name": "critical_evaluation.md", "title": "Teaching Critical Evaluation"},
                {"name": "essay_skills.md", "title": "Extended Writing and AO3 Skills"},
                {"name": "ethical_considerations.md", "title": "Teaching Ethical Considerations"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Psychology Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Psychology Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "bps.md", "title": "British Psychological Society and Education"},
                {"name": "atp.md", "title": "Association for the Teaching of Psychology"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Psychology Topics"},
                {"name": "progression.md", "title": "Progression from GCSE to A Level Psychology"},
            ]},
        ],
    },

    "economics": {
        "name": "Economics",
        "folder": "economics-curriculum",
        "thinkers": [
            {"name": "Alain Anderton", "focus": "A Level economics textbooks, Pearson, accessible economics pedagogy"},
            {"name": "Peter Smith", "focus": "economics education, textbooks, teaching quantitative skills"},
            {"name": "Jim Riley", "focus": "Tutor2u founder, economics resources, exam technique, digital pedagogy"},
            {"name": "Nancy Wall", "focus": "Nuffield economics, critical thinking, ethics in economics education"},
            {"name": "Ha-Joon Chang", "focus": "Cambridge, heterodox economics, institutional economics, accessible writing"},
        ],
        "categories": [
            {"folder": "01_curriculum_overview", "label": "Curriculum Overview", "files": [
                {"name": "overview.md", "title": "Economics Curriculum Overview"},
                {"name": "ks4.md", "title": "Economics at Key Stage 4 (GCSE)"},
                {"name": "ks5.md", "title": "Economics at Key Stage 5 (A Level)"},
            ]},
            {"folder": "02_subject_knowledge", "label": "Subject Knowledge", "files": [
                {"name": "microeconomics.md", "title": "Microeconomics"},
                {"name": "macroeconomics.md", "title": "Macroeconomics"},
                {"name": "market_failure.md", "title": "Market Failure and Government Intervention"},
                {"name": "international_economics.md", "title": "International Economics and Trade"},
                {"name": "labour_market.md", "title": "The Labour Market"},
                {"name": "financial_markets.md", "title": "Financial Markets and Monetary Policy"},
            ]},
            {"folder": "03_key_thinkers", "label": "Key Thinkers", "files": "AUTO"},
            {"folder": "04_pedagogy", "label": "Pedagogy", "files": [
                {"name": "diagrams_and_models.md", "title": "Teaching Economic Diagrams and Models"},
                {"name": "quantitative_skills.md", "title": "Quantitative Skills in Economics"},
                {"name": "current_affairs.md", "title": "Using Current Affairs in Economics Teaching"},
                {"name": "essay_skills.md", "title": "Extended Writing and Evaluation Skills"},
            ]},
            {"folder": "05_assessment", "label": "Assessment", "files": [
                {"name": "gcse_specifications.md", "title": "GCSE Economics Specifications"},
                {"name": "a_level_specifications.md", "title": "A Level Economics Specifications"},
            ]},
            {"folder": "06_resources_and_organisations", "label": "Resources and Organisations", "files": [
                {"name": "rea.md", "title": "Royal Economic Society and Economics Education"},
                {"name": "tutor2u_economics.md", "title": "Tutor2u Economics Resources"},
                {"name": "ebea.md", "title": "Economics, Business and Enterprise Association"},
            ]},
            {"folder": "07_curriculum_architecture", "label": "Curriculum Architecture", "files": [
                {"name": "sequencing.md", "title": "Sequencing Economics Topics"},
                {"name": "progression.md", "title": "Progression from GCSE to A Level Economics"},
            ]},
        ],
    },
}


# ─────────────────────────────────────────────────────────────
# GENERATION ENGINE
# ─────────────────────────────────────────────────────────────

def _get_files_for_category(subject_cfg, cat):
    """Resolve file list for a category (handles AUTO for key_thinkers)."""
    if cat["files"] == "AUTO":
        return [
            {"name": f"{t['name'].lower().replace(' ', '_').replace('-', '_')}.md",
             "title": t["name"]}
            for t in subject_cfg["thinkers"]
        ]
    return cat["files"]


def _build_prompt(subject_cfg, cat, file_info, is_thinker=False):
    """Build the generation prompt for a single file."""
    subject = subject_cfg["name"]
    thinker_names = ", ".join(t["name"] for t in subject_cfg["thinkers"])

    if is_thinker:
        thinker = next(
            (t for t in subject_cfg["thinkers"]
             if t["name"].lower().replace(" ", "_").replace("-", "_")
             == file_info["name"].replace(".md", "")),
            None
        )
        focus = thinker["focus"] if thinker else ""
        return f"""Write a comprehensive expert knowledge file about {file_info['title']} and their contribution to {subject} education in the UK.

This person's focus areas: {focus}

Structure the file with:
- Full name, current roles, known for (at the top)
- Biography section with career history
- Key Ideas section (numbered, with detailed explanations)
- Key Publications section
- Influence on curriculum and policy
- Pedagogical approach
- Sources section

Use UK English throughout. Be detailed and specific — cite their actual publications, frameworks, and concepts.
Aim for 150-250 lines of markdown. Use ## for main sections, ### for subsections.
Start with # {file_info['title']} as the top heading."""

    return f"""Write a comprehensive expert knowledge file for UK {subject} education on the topic: {file_info['title']}

This is part of the {cat['label']} section of a {subject} curriculum knowledge base.

Key thinkers in this subject include: {thinker_names}
Reference these thinkers where relevant.

Structure with clear markdown headings (## and ###).
Include:
- Specific UK National Curriculum references where relevant
- Key stage breakdowns where appropriate
- Practical implications for teachers
- Research evidence and expert opinion
- UK exam board references (AQA, Edexcel, OCR, WJEC) where applicable

Use UK English throughout. Be detailed and specific.
Aim for 100-200 lines of markdown. Start with # {file_info['title']} as the top heading."""


def generate_subject(subject_key, dry_run=False):
    """Generate all expert input files for a single subject."""
    from ai_client import create_message

    if subject_key not in SUBJECTS:
        print(f"❌ Unknown subject: {subject_key}")
        print(f"Available: {', '.join(sorted(SUBJECTS.keys()))}")
        return 0

    cfg = SUBJECTS[subject_key]
    subj_dir = OUTPUT_DIR / cfg["folder"]
    total_files = 0
    generated = 0
    skipped = 0

    for cat in cfg["categories"]:
        files = _get_files_for_category(cfg, cat)
        cat_dir = subj_dir / cat["folder"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        is_thinker = cat["files"] == "AUTO"

        for file_info in files:
            total_files += 1
            out_path = cat_dir / file_info["name"]

            if out_path.exists() and out_path.stat().st_size > 100:
                skipped += 1
                continue

            if dry_run:
                print(f"  [DRY] {cat['folder']}/{file_info['name']}")
                continue

            prompt = _build_prompt(cfg, cat, file_info, is_thinker=is_thinker)

            try:
                response = create_message(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4000,
                    system=[{
                        "type": "text",
                        "text": (
                            f"You are an expert in UK {cfg['name']} curriculum and education. "
                            "Write detailed, authoritative knowledge-base files for teachers and "
                            "curriculum leaders. Always use UK English. Be specific — cite real "
                            "publications, frameworks, and researchers by name."
                        ),
                    }],
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text.strip()
                out_path.write_text(content, encoding="utf-8")
                generated += 1
                print(f"  ✅ {cat['folder']}/{file_info['name']} ({len(content)} chars)")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"  ❌ {cat['folder']}/{file_info['name']}: {e}")

    print(f"\n{cfg['name']}: {generated} generated, {skipped} skipped (already exist), {total_files} total")
    return generated


def import_to_reference_library():
    """Import all generated files into the app's Reference Library."""
    from reference_library import save_document, list_documents

    SUBJECT_NAME_MAP = {cfg["folder"]: cfg["name"] for cfg in SUBJECTS.values()}

    imported = 0
    errors = 0

    for subj_folder in sorted(OUTPUT_DIR.iterdir()):
        if not subj_folder.is_dir():
            continue

        subject_name = SUBJECT_NAME_MAP.get(subj_folder.name, subj_folder.name)

        for cat_folder in sorted(subj_folder.iterdir()):
            if not cat_folder.is_dir():
                continue

            cat_name = cat_folder.name
            if len(cat_name) > 3 and cat_name[2] == '_':
                cat_name = cat_name[3:]
            cat_label = cat_name.replace("_", " ").title()

            for md_file in sorted(cat_folder.glob("*.md")):
                if md_file.stat().st_size < 50:
                    continue

                file_title = md_file.stem.replace("_", " ").title()
                title = f"{subject_name} — {cat_label} — {file_title}"

                try:
                    save_document(
                        file_path=str(md_file),
                        category="expert_input",
                        title=title,
                        subject=subject_name,
                        description=f"Expert input: {cat_label} / {file_title}",
                    )
                    imported += 1
                except Exception as e:
                    # Might already exist
                    errors += 1

    print(f"\n✅ Imported {imported} files ({errors} errors/duplicates)")
    docs = list_documents()
    print(f"📚 Reference Library now has {len(docs)} documents total")


def regenerate_thinkers(subject_key=None):
    """Regenerate key thinker files for one or all subjects, overwriting existing.

    Unlike generate_subject(), this forcibly overwrites the thinker markdown files
    so they can be periodically refreshed with up-to-date content.

    Returns dict: {"generated": int, "errors": int, "subjects": [str]}
    """
    from ai_client import create_message
    from reference_library import save_document

    keys = [subject_key] if subject_key else sorted(SUBJECTS.keys())
    total_generated = 0
    total_errors = 0
    subjects_done = []

    for key in keys:
        if key not in SUBJECTS:
            continue

        cfg = SUBJECTS[key]
        subj_dir = OUTPUT_DIR / cfg["folder"]

        # Find the key_thinkers category (the one with files == "AUTO")
        thinker_cat = None
        for cat in cfg["categories"]:
            if cat["files"] == "AUTO":
                thinker_cat = cat
                break

        if not thinker_cat:
            continue

        files = _get_files_for_category(cfg, thinker_cat)
        cat_dir = subj_dir / thinker_cat["folder"]
        cat_dir.mkdir(parents=True, exist_ok=True)

        for file_info in files:
            out_path = cat_dir / file_info["name"]
            prompt = _build_prompt(cfg, thinker_cat, file_info, is_thinker=True)

            try:
                response = create_message(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4000,
                    system=[{
                        "type": "text",
                        "text": (
                            f"You are an expert in UK {cfg['name']} curriculum and education. "
                            "Write detailed, authoritative knowledge-base files for teachers and "
                            "curriculum leaders. Always use UK English. Be specific — cite real "
                            "publications, frameworks, and researchers by name."
                        ),
                    }],
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text.strip()
                out_path.write_text(content, encoding="utf-8")
                total_generated += 1

                # Also update in Reference Library
                file_title = file_info["name"].replace(".md", "").replace("_", " ").title()
                title = f"{cfg['name']} — Key Thinkers — {file_title}"
                try:
                    save_document(
                        file_path=str(out_path),
                        category="expert_input",
                        title=title,
                        subject=cfg["name"],
                        description=f"Expert input: Key Thinkers / {file_title}",
                    )
                except Exception:
                    pass  # already exists — fine

                time.sleep(0.5)
            except Exception as e:
                total_errors += 1
                print(f"  ❌ {cfg['name']}/{file_info['name']}: {e}")

        subjects_done.append(cfg["name"])
        print(f"  ✅ {cfg['name']}: {len(files)} thinker files regenerated")

    return {
        "generated": total_generated,
        "errors": total_errors,
        "subjects": subjects_done,
    }


def list_subjects():
    """List all available subjects and their status."""
    print(f"\n{'Subject':<25} {'Key':<15} {'Files':<8} {'Generated':<10}")
    print("-" * 60)
    for key, cfg in sorted(SUBJECTS.items()):
        total = sum(
            len(_get_files_for_category(cfg, cat))
            for cat in cfg["categories"]
        )
        subj_dir = OUTPUT_DIR / cfg["folder"]
        existing = len(list(subj_dir.rglob("*.md"))) if subj_dir.exists() else 0
        status = "✅" if existing >= total else f"{existing}/{total}"
        print(f"{cfg['name']:<25} {key:<15} {total:<8} {status:<10}")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate expert input files for UK curriculum subjects")
    parser.add_argument("--subject", "-s", help="Generate files for a specific subject key")
    parser.add_argument("--all", action="store_true", help="Generate files for ALL subjects")
    parser.add_argument("--list", "-l", action="store_true", help="List available subjects")
    parser.add_argument("--import", "-i", dest="do_import", action="store_true", help="Import generated files into Reference Library")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without doing it")
    args = parser.parse_args()

    if args.list:
        list_subjects()
    elif args.do_import:
        import_to_reference_library()
    elif args.subject:
        generate_subject(args.subject, dry_run=args.dry_run)
    elif args.all:
        for key in sorted(SUBJECTS.keys()):
            print(f"\n{'='*60}")
            print(f"Generating: {SUBJECTS[key]['name']}")
            print(f"{'='*60}")
            generate_subject(key, dry_run=args.dry_run)
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  python generate_expert_input.py --list")
        print("  python generate_expert_input.py --subject computing")
        print("  python generate_expert_input.py --all")
        print("  python generate_expert_input.py --import")
