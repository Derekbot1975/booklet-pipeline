# Programming Concepts and Progression

## Introduction

Programming forms one of the three core strands of the National Curriculum for Computing in England, alongside Computer Science concepts and Information Technology skills. The progression from simple instructions in Early Years to complex algorithmic thinking at Key Stage 4 represents a significant pedagogical challenge. This knowledge file synthesises research from key UK Computing education thinkers and provides a framework for understanding and teaching programming concepts across the key stages.

## The Computing at School Progression Pathways Framework

The Computing at School (CAS) community, led by thinkers including **Mark Dorling** and **Miles Berry**, developed progression pathways that have become foundational to UK Computing education. These pathways identify incremental stages of learning from age 5 to 16+, providing teachers with granular progression steps beyond the statutory National Curriculum statements.

**Mark Dorling's** research emphasises that programming progression should be viewed as a continuum rather than discrete jumps between key stages. His work on computational thinking highlights that programming is fundamentally about problem decomposition, pattern recognition, abstraction, and algorithmic design—concepts that develop gradually across a child's education.

## Key Stage Progression Overview

### Early Years Foundation Stage (EYFS)

Although not formally part of Computing, EYFS lays foundations through:
- **Sequencing activities**: Following multi-step instructions (e.g., making a sandwich)
- **Spatial reasoning**: Understanding positional language (forwards, backwards, left, right)
- **Cause and effect**: Understanding that actions have consequences

**Phil Bagge**, a prominent Computing educator and author of "Computing for the National Curriculum," emphasises that physical embodiment of algorithms (e.g., children acting as robots following instructions) provides essential pre-programming experiences.

### Key Stage 1 (Ages 5-7)

The National Curriculum states that pupils should:
- "Understand what algorithms are; how they are implemented as programs on digital devices; and that programs execute by following precise and unambiguous instructions"
- "Create and debug simple programs"
- "Use logical reasoning to predict the behaviour of simple programs"

**Progression in Programming Concepts:**

**Algorithms and Sequencing**: Children begin with unplugged activities (writing instructions for making tea, directing a friend through an obstacle course) before moving to simple programming environments like Bee-Bot or Blue-Bot. These floor robots provide tangible feedback and help children understand that computers execute instructions exactly as given.

**Debugging**: At this stage, debugging is primarily about spotting and correcting incorrect sequences. **Miles Berry** notes that developing a "debugging mindset"—where errors are seen as learning opportunities—is crucial from the earliest stages.

**Practical Implications**: Use block-based programming environments (Scratch Jr, ScratchJr, or Code.org's Course A/B) that provide immediate visual feedback. Maintain strong links between unplugged and plugged activities.

### Key Stage 2 (Ages 7-11)

The National Curriculum requires pupils to:
- "Design, write and debug programs that accomplish specific goals"
- "Use sequence, selection, and repetition in programs"
- "Use logical reasoning to explain how some simple algorithms work and to detect and correct errors"
- "Use variables to store and manipulate data"

**Progression in Programming Concepts:**

**Sequence, Selection, and Repetition**: These three fundamental control structures (described by **Simon Peyton Jones**, Chair of Computing at School, as "the building blocks of all programming") are introduced progressively:

- **Years 3-4**: Master definite iteration (repeat n times, for loops) and simple conditional statements (if-then)
- **Years 5-6**: Develop understanding of indefinite iteration (while/until loops), nested conditionals (if-then-else), and complex Boolean conditions

**Variables and Data**: **Sue Sentance**, Director of Raspberry Pi Computing Education Research Centre, has conducted extensive research showing that variables represent a significant conceptual threshold. Her studies indicate that children often struggle with:
- The distinction between a variable's name and its value
- Understanding assignment versus equality
- The concept that variables can change during program execution

Progression typically moves from:
1. Using variables as fixed values (scores, names)
2. Modifying variables through direct input
3. Using variables in calculations and reassignment
4. Understanding scope (local vs global variables—introduced cautiously at upper KS2)

**Practical Implications**: Scratch (MIT's block-based environment) is the dominant tool at KS2, endorsed by CAS and recommended by many local authority schemes of work. **Phil Bagge's** "Code-IT" materials provide excellent structured progression through Scratch, introducing concepts incrementally with well-designed tasks.

Teachers should use **PRIMM pedagogy** (Predict, Run, Investigate, Modify, Make), developed by **Sue Sentance** and colleagues at King's College London, to scaffold programming activities effectively.

### Key Stage 3 (Ages 11-14)

The National Curriculum states pupils should:
- "Use two or more programming languages, at least one of which is textual, to solve a variety of computational problems"
- "Understand simple Boolean logic and its application in programming"
- "Use data structures appropriately"

**Progression in Programming Concepts:**

**Transition to Text-Based Languages**: This transition represents a significant pedagogical challenge. Research by **Sue Sentance** suggests a gradual approach:
- Year 7: Consolidate block-based programming while introducing text-based syntax through hybrid environments (e.g., Scratch's "See Inside" feature, or Python with Trinket)
- Year 8: Python becomes the primary language for most UK schools, following CAS recommendations
- Year 9: Deepen understanding with more complex problems and potentially introduce a second language (JavaScript, HTML/CSS, SQL)

**Boolean Logic**: **Simon Peyton Jones** emphasises that Boolean logic is fundamental to both programming and wider Computer Science. Progression includes:
- Simple Boolean operators (AND, OR, NOT)
- Truth tables and logical expressions
- Application in complex conditional statements
- Connection to selection in algorithms and database queries

**Data Structures**: Moving beyond simple variables to:
- **Lists/Arrays**: One-dimensional collections (Year 7-8)
- **2D Arrays**: Introduction to nested structures (Year 8-9)
- **Records/Dictionaries**: Key-value pairs (Year 9)

**Subroutines and Procedures**: Introducing functions/procedures with parameters and return values. **Mark Dorling's** work emphasises that understanding abstraction through subroutines is crucial for managing complexity.

**Practical Implications**: Python is overwhelmingly the language of choice for KS3, supported by resources from Raspberry Pi Foundation, Code Club, and numerous textbooks. Replit, Trinket, and IDLE are common development environments.

Teachers should explicitly teach programming constructs rather than assuming discovery through project work. **Sue Sentance's** research on block-based versus text-based transition indicates that explicit teaching of syntax, combined with regular practice, produces better outcomes than project-only approaches.

### Key Stage 4 (Ages 14-16, GCSE)

All major exam boards (AQA, OCR, Edexcel/Pearson, WJEC/Eduqas) require comprehensive programming competence:

**Core Programming Concepts Required:**

**AQA 8525 and OCR J277** specifications require:
- Data types (integer, real, Boolean, character, string)
- Operators (arithmetic, comparison, logical)
- Sequence, selection, iteration (definite and indefinite)
- String manipulation and handling
- Arrays (1D and 2D) and records
- Subroutines with parameters
- File handling
- SQL for database queries

**Edexcel 1CP2** and **WJEC Eduqas** have similar requirements with slight variations in emphasis.

**Programming Languages**: While specifications are language-agnostic, most schools use Python, with some teaching VB.NET or C#. OCR provides resources specifically for Python, VB.NET, and C#.

**Practical Programming Assessment**: OCR includes a 20-hour programming project (worth 20% of GCSE), whilst AQA, Edexcel, and WJEC assess programming through written examination with some practical programming in controlled assessment format.

**Advanced Concepts:**

**Algorithms**: GCSE students must understand standard algorithms:
- Linear and binary search (**OCR** and **AQA** explicitly require these)
- Bubble sort and merge sort (understanding efficiency—Big O notation introduced at higher tier)
- **Simon Peyton Jones** argues that algorithmic thinking—understanding why algorithms work and comparing their efficiency—distinguishes Computer Science from mere coding

**Object-Oriented Programming**: Not explicitly required at GCSE but introduced in some schools preparing for A-level progression.

**Practical Implications**: Teachers must balance teaching programming constructs with developing problem-solving skills. **Sue Sentance's** PRIMM approach remains relevant. Regular short programming exercises ("code katas") alongside longer projects develops both fluency and problem-solving capability.

## Threshold Concepts in Programming

Research identifies several **threshold concepts**—ideas that transform student understanding but present particular difficulty:

### Variables and Assignment

**Sue Sentance's** research identifies five key difficulties:
1. **Assignment vs equality**: Understanding that `=` means "assign" not "equals"
2. **Variable modification**: Understanding `x = x + 1` requires recognising temporal sequence
3. **Symbolic representation**: The variable name is not the value itself
4. **Scope**: Variables exist within certain contexts
5. **Type**: Different data types have different properties and operations

**Teaching Implications**: Use concrete analogies (labelled boxes), trace tables showing state changes, and extensive worked examples before independent practice.

### Loops and Iteration

**Mark Dorling's** progression framework identifies stages:
1. **Fixed repetition** (repeat 5 times)—typically Year 3-4
2. **Count-controlled** (for i in range)—Year 4-5
3. **Condition-controlled** (while/until)—Year 5-6
4. **Nested loops**—Year 6-7

Common misconceptions include confusing loop types and misunderstanding loop termination conditions.

### Selection and Boolean Logic

**Phil Bagge** emphasises starting with single conditions before nested or complex logical expressions. The progression:
1. Simple if statements (if raining then...)
2. If-then-else structures
3. Elif/else-if chains
4. Nested conditionals
5. Complex Boolean expressions with AND/OR/NOT

### Functions and Abstraction

Understanding functions requires grasping:
- **Information hiding**: Internal implementation details don't matter to the function user
- **Parameters and arguments**: The distinction between defining and calling
- **Return values**: Functions produce outputs
- **Scope**: Variables inside functions are separate from outside

This concept typically develops across Years 7-9.

## Pedagogical Approaches

### PRIMM (Predict, Run, Investigate, Modify, Make)

Developed by **Sue Sentance** and colleagues through research at King's College London and Raspberry Pi Foundation, PRIMM provides structured scaffolding:

**Predict**: Students read code and predict outcomes before running
**Run**: Execute and compare predictions with actual behaviour
**Investigate**: Answer questions requiring detailed code examination
**Modify**: Make specified changes to existing code
**Make**: Create own programs from scratch

Research evidence shows PRIMM improves outcomes, particularly for students who struggle with open-ended programming tasks.

### Unplugged to Plugged Progression

**Phil Bagge** and **Miles Berry** advocate beginning concepts with unplugged activities:
- Algorithms: Written instructions, physical direction-giving
- Debugging: Spot-the-mistake in written instructions
- Selection: Flowcharts and decision trees
- Variables: Labelled boxes with changeable contents

These concrete representations support abstract understanding when transitioning to screen-based programming.

### Use-Modify-Create Framework

This pedagogical progression, supported by **CAS** guidance:
**Use**: Experience and explore existing programs
**Modify**: Adapt and change programs with support
**Create**: Design and build programs independently

Teachers should ensure students don't skip to "Create" without adequate "Use" and "Modify" experiences.

## Common Misconceptions and Difficulties

### Syntax vs Semantics

Students often confuse syntax errors (violations of language rules) with semantic errors (code that runs but doesn't do what's intended). **Sue Sentance's** research suggests explicit teaching of this distinction improves debugging capability.

### Sequential Execution Model

Students may struggle understanding that computers execute one instruction at a time in sequence (unless explicitly controlled by selection/iteration structures). **Mark Dorling** recommends trace tables and step-through debugging tools.

### Abstraction Levels

The gap between low-level computer operations and high-level programming constructs challenges many students. **Simon Peyton Jones** advocates teaching the "semantic gap"—how high-level constructs translate to machine operations—particularly at KS4.

## Assessment and Progression Monitoring

### Formative Assessment Strategies

**Diagnostic Questions**: CAS community has developed banks of programming-specific diagnostic questions that reveal common misconceptions.

**Code Tracing**: Students trace program execution, showing variable values at each step. This assessment technique, recommended by **Sue Sentance**, reveals understanding of program flow.

**Explain-in-Plain-English**: Students describe what code does in everyday language, demonstrating comprehension beyond syntax memorisation.

**Pair Programming**: Research shows peer programming improves outcomes when structured appropriately (one driver, one navigator, regular role-switching).

### Progression Indicators

**Mark Dorling's** CAS progression pathways identify specific indicators at each stage, allowing teachers to assess whether students are working at expected levels. For instance:
- **Year 3 expectation**: "Uses repeat commands with loops"
- **Year 7 expectation**: "Understands that iteration is the repetition of a process"
- **Year 9 expectation**: "Recognises where there is common functionality in a program and uses subroutines to reduce code duplication"

## Research Evidence and Effective Practice

### The Fragile Knowledge Problem

Research by **Sue Sentance** and colleagues indicates programming knowledge is often "fragile"—students may complete tasks successfully but struggle to transfer learning to new contexts. Solutions include:
- **Spaced practice**: Revisiting concepts regularly rather than single intensive teaching blocks
- **Varied contexts**: Teaching concepts across different problems and domains
- **Explicit connections**: Teachers making links between concepts explicit

### Productive Failure and Debugging Culture

**Phil Bagge** and **Miles Berry** emphasise creating classroom cultures where errors are normalised. Research shows that students who engage productively with error messages and debug systematically develop stronger programming competence than those who avoid errors.

### Cognitive Load Considerations

Complex programming environments can overwhelm working memory. **CAS** guidance recommends:
- Minimise split attention (code and output visible simultaneously)
- Reduce redundancy (hide irrelevant environment features)
- Use worked examples extensively before independent practice
- Scaffold complex tasks with partially-completed programs

## Practical Resources and Environment Selection

### Key Stage 1-2
- **Bee-Bot/Blue-Bot**: Physical programming introduction
- **ScratchJr**: Block-based programming for age 5-7
- **Scratch**: Block-based programming for age 8-11 (MIT, supported by Raspberry Pi Foundation)
- **Purple Mash/2Code**: Scheme-of-work-aligned tools

### Key Stage 3-4
- **Python**: Text-based language (Python Software Foundation, supported by extensive UK resources)
- **Replit, Trinket, Mu Editor**: Programming environments
- **Raspberry Pi**: Physical computing integration
- **Project Quantum (OCR)**: GCSE teaching resources
- **Isaac Computer Science**: University of Cambridge supported resource

### Professional Development Resources
- **National Centre for Computing Education (NCCE)**: Government-funded CPD, including programming pedagogy courses developed by Raspberry Pi Foundation
- **CAS Community**: Teacher resource sharing and support
- **Barefoot Computing**: Primarily for primary teachers

## Conclusion

Programming progression in UK Computing education represents a carefully constructed journey from concrete physical instructions through block-based environments to sophisticated text-based programming. Research by **Sue Sentance**, **Mark Dorling**, **Simon Peyton Jones**, **Phil Bagge**, and **Miles Berry** has established evidence-based approaches that recognise programming as both intellectually demanding and accessible to all learners when taught systematically.

Teachers must understand that programming competence develops incrementally, that threshold concepts require explicit teaching and extensive practice, and that pedagogy matters enormously. The PRIMM framework, unplugged-to-plugged progression, and Use-Modify-Create approaches provide structured methodologies that research shows are effective.

Ultimately, programming education serves the broader purpose of developing computational thinking—the problem-solving approaches transferable far beyond computer screens. As **Simon Peyton Jones** argues, programming is "the Latin of the 21st century"—a discipline that develops rigorous thinking applicable across domains.