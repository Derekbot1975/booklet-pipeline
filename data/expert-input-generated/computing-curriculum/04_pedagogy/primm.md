# The PRIMM Framework (Predict-Run-Investigate-Modify-Make)

## Overview and Origins

The PRIMM framework is a pedagogical approach specifically designed for teaching programming in Computing education. Developed by Sue Sentance and Andrew Csizmadia at King's College London, with subsequent development through the National Centre for Computing Education (NCCE), PRIMM provides a structured methodology for introducing learners to new programming concepts through careful scaffolding.

The framework emerged from research conducted by the Centre for Computing Education Research at King's College London, published in 2019, and has since become one of the most influential pedagogical approaches in UK Computing education. Sue Sentance, in particular, has been instrumental in promoting evidence-based Computing pedagogy, and PRIMM represents a synthesis of research on worked examples, comprehension activities, and constructivist learning theory.

The framework addresses a fundamental challenge identified by researchers including Mark Dorling and Simon Peyton Jones: that learners often struggle when asked to write code from scratch without sufficient grounding in reading and understanding existing code first.

## The Five Stages of PRIMM

### 1. Predict

In the Predict phase, learners are presented with a complete, working code example without running it. They must examine the code carefully and predict what it will do when executed. This stage emphasises:

- **Code comprehension before execution**: Learners develop the ability to trace through code mentally, a critical skill identified by computing education researchers
- **Discussion and reasoning**: Students articulate their predictions, ideally in pairs or small groups, explaining their thinking
- **Misconception identification**: Teachers can identify student misunderstandings before they become embedded

The Predict stage draws on research by du Boulay (1986) and subsequent work by Sorva (2012) on notional machines – the conceptual model learners build of how code executes. Sue Sentance emphasises that prediction activities help students construct accurate mental models of program execution.

**Practical implementation**: Teachers should provide partially annotated code with strategic comments, use think-aloud protocols, and encourage students to write down predictions with justifications. For Key Stage 3, predictions might focus on output values; for Key Stage 4 and 5, predictions could extend to efficiency, side effects, or exception handling.

### 2. Run

The Run phase involves executing the code and comparing actual outcomes with predictions. This stage:

- **Provides immediate feedback**: Students verify or revise their understanding based on concrete results
- **Encourages debugging mindset**: Discrepancies between predictions and outcomes become learning opportunities
- **Builds empirical understanding**: Learners see the actual behaviour of programming constructs

Teachers should facilitate structured observation during this phase. At Key Stage 3, students might use tools like Scratch, Python IDLE, or Repl.it with clear visibility of outputs. At Key Stage 4, students working toward GCSE qualifications (AQA 8525, OCR J277, Edexcel 1CP2, WJEC Eduqas C500QS) should develop systematic approaches to testing predictions.

**Practical considerations**: Use of debuggers, visualisation tools like Python Tutor, and step-through execution helps students develop the "notional machine" concept discussed by Sentance and Csizmadia. Phil Bagge's work on physical computing and tangible outputs can make the Run phase particularly engaging at KS2-3.

### 3. Investigate

The Investigate phase deepens comprehension through structured exploration. Students examine the code more systematically, identifying:

- **Key programming constructs**: Variables, control structures, data types, functions
- **Code patterns and idioms**: Common programming techniques and structures
- **Relationships between code sections**: How different parts interact

This phase aligns with the UK National Curriculum requirements for Key Stage 3: "understand several key algorithms... use two or more programming languages, at least one of which is textual." The investigation phase helps students recognise patterns transferable across languages.

Sue Sentance's research emphasises the importance of **targeted questioning** during investigation. Teachers should prepare specific questions that draw attention to:

- Syntax patterns (e.g., "What punctuation is used to end each Python statement?")
- Semantic meaning (e.g., "Why does the loop use `range(10)` rather than `range(11)`?")
- Design decisions (e.g., "Why might the programmer have chosen a while loop here?")

**Differentiation strategies**: For higher-attaining students at Key Stage 4/5, investigate activities might include comparing multiple solutions to the same problem, examining time/space complexity, or evaluating code quality against established standards. Miles Berry's work on computational thinking emphasises how investigation activities develop pattern recognition and abstraction skills.

### 4. Modify

The Modify phase involves making purposeful, guided changes to the existing code. This scaffolded approach:

- **Reduces cognitive load**: Students work with a functioning foundation rather than starting from scratch
- **Builds confidence incrementally**: Success with small modifications motivates further learning
- **Develops debugging skills**: Students learn to fix broken modifications

Modification tasks should be carefully sequenced from simple to complex:

**Level 1 modifications** (suitable for KS3 beginners): Changing literal values (e.g., modifying a score threshold, changing output text)

**Level 2 modifications** (KS3/KS4): Adapting logic (e.g., changing conditions in if statements, adding additional elif branches)

**Level 3 modifications** (KS4/KS5): Restructuring code (e.g., converting a while loop to a for loop, refactoring repeated code into functions)

**Level 4 modifications** (A-Level, particularly OCR H446, AQA 7517): Optimising algorithms, implementing additional features, or adapting code for different data structures

Sue Sentance notes that modification activities address the "near transfer problem" – helping students apply knowledge in slightly different contexts before attempting far transfer (creating entirely new programs).

### 5. Make

The Make phase represents the culmination of PRIMM, where students create their own programs from scratch, applying the concepts they've learned through the previous four stages. This final phase:

- **Develops creative problem-solving**: Students design solutions to novel problems
- **Builds confidence in independent programming**: Having progressed through scaffolded stages, students are better prepared for independent work
- **Enables authentic assessment**: Teachers can evaluate genuine understanding

The Make phase aligns directly with NC Programme of Study requirements: "design, use and evaluate computational abstractions that model the state and behaviour of real-world problems and physical systems."

**Progression considerations**: 

For **Key Stage 3**, Make tasks might involve creating a simple game, interactive story, or data processing program building on investigated concepts.

For **GCSE** (all exam boards require substantial programming projects), Make activities should incorporate requirements from the specification: user input validation, file handling, appropriate data structures (particularly for higher tier).

For **A-Level** (AQA 7517, OCR H446, WJEC A680QS), the Make phase should develop substantial programs demonstrating object-oriented design, algorithm implementation, and system integration skills required for the NEA (Non-Examined Assessment).

## Theoretical Foundations and Research Evidence

### Cognitive Load Theory

PRIMM is grounded in Cognitive Load Theory (Sweller, 1988), which explains how working memory limitations affect learning. Sue Sentance and colleagues explicitly reference this in their research, noting that asking novices to write code from scratch imposes excessive cognitive load. The scaffolded progression through PRIMM stages manages cognitive load by:

- **Reducing extraneous load**: Students aren't simultaneously learning syntax, semantics, problem decomposition, and debugging
- **Optimising germane load**: Each stage focuses attention on specific aspects of programming understanding
- **Providing worked examples**: The Predict and Investigate stages utilise the worked example effect documented by Sweller

### The SOLO Taxonomy and Progression

PRIMM stages map onto the Structure of Observed Learning Outcomes (SOLO) taxonomy (Biggs and Collis, 1982), supporting clear progression:

- **Predict/Run**: Unistructural understanding (identifying single elements)
- **Investigate**: Multistructural understanding (identifying multiple independent elements)
- **Modify**: Relational understanding (integrating elements)
- **Make**: Extended abstract understanding (applying to novel contexts)

### Code-Reading Before Code-Writing

Research by Lister et al. (2004) and subsequent studies demonstrate that novice programmers often cannot read and comprehend code effectively, yet are asked to write it. Mark Dorling's work on Computing progression frameworks emphasises that code comprehension must precede code generation. PRIMM addresses this by making code reading explicit and systematic.

Sue Sentance's research with secondary school students (2019) found that classes using PRIMM showed significantly improved code comprehension and programming confidence compared to control groups using traditional "explain then practice" approaches.

### Semantic Waves and Knowledge Building

Building on Maton's Legitimation Code Theory (2013), Sue Sentance describes how PRIMM creates "semantic waves" – oscillating between concrete examples (Predict/Run) and abstract principles (Investigate), then back to concrete application (Modify/Make). This movement between abstraction levels, endorsed by Miles Berry's work on Computing pedagogy, helps students build robust, transferable knowledge.

## Practical Implementation Strategies

### Lesson Planning with PRIMM

A complete PRIMM cycle typically spans multiple lessons. Sue Sentance recommends:

**Single lesson PRIMM** (suitable for introducing small, discrete concepts at KS3):
- 10 minutes: Predict (pairs discussion, whole-class sharing)
- 5 minutes: Run (observe and verify)
- 15 minutes: Investigate (guided questions, annotation)
- 15 minutes: Modify (two or three increasingly challenging modifications)
- 5 minutes: Review and preview Make task for homework

**Extended PRIMM** (suitable for complex concepts at KS4/5):
- Lesson 1: Predict, Run, Investigate thoroughly with multiple examples
- Lesson 2: Modify with increasingly open-ended tasks
- Lesson 3-4: Make, with teacher support and peer review

### Selecting Code Examples

The quality of the initial code example is crucial. Effective PRIMM examples should:

- **Be complete and correct**: The code must run without errors
- **Illustrate clearly**: The code should exemplify the concept without extraneous complexity
- **Be purposeful**: The code should solve a meaningful problem, not be arbitrary
- **Support prediction**: The code should be comprehensible without execution
- **Enable modification**: The structure should accommodate the planned modifications

Phil Bagge's resources (published through Computing at School and Barefoot Computing) provide excellent examples of PRIMM-suitable code for primary-secondary transition and early KS3.

### Assessment and PRIMM

PRIMM enables diverse assessment opportunities:

**Formative assessment**:
- Predict phase: Assessing mental models through prediction accuracy and reasoning
- Investigate phase: Evaluating comprehension through questioning responses
- Modify phase: Gauging understanding through success with increasingly complex modifications

**Summative assessment**:
- Make phase: Traditional programming tasks, now more valid as students have adequate preparation
- Portfolio evidence: GCSE and A-Level programming projects (NEA components) can document progression through PRIMM stages

OCR's Project Qualification in Programming (J807) particularly benefits from PRIMM approaches, as it requires evidence of iterative development – naturally documented through Modify and Make stages.

### Differentiation and Inclusion

PRIMM supports differentiation effectively:

**For students requiring additional support**:
- Extended time on Predict/Investigate phases
- Simplified modification tasks with explicit hints
- Paired programming during Modify phase
- Scaffolded Make tasks with partial solutions provided

**For higher-attaining students**:
- Multiple example investigation (comparing different solutions)
- Open-ended modification challenges
- Earlier transition to Make phase
- Extension Make tasks involving optimisation or feature enhancement

Sue Sentance's research emphasises that PRIMM benefits all students but particularly supports those who struggle with traditional "copy the teacher's example" approaches. Students with weak working memory or processing difficulties benefit from the reduced cognitive load, while the structured progression prevents capable students from developing misconceptions through premature independent work.

### Common Pitfalls and Solutions

**Pitfall 1: Rushing through early stages**
Teachers familiar with the code may accelerate through Predict/Investigate, but Sue Sentance warns this undermines the framework's effectiveness. Solution: Time predictions generously; require written predictions; use think-pair-share protocols.

**Pitfall 2: Modifications too challenging**
Jumping from simple parameter changes to complex logic modifications loses the scaffolding benefit. Solution: Plan 4-6 modifications with gradual difficulty increase; have extension modifications ready.

**Pitfall 3: Make tasks disconnected from earlier stages**
If Make tasks don't build on investigated concepts, the scaffolding collapses. Solution: Ensure Make tasks explicitly require the construct/pattern from Predict-Modify stages.

**Pitfall 4: Inadequate investigation**
Treating investigation as a quick "look at the code" activity misses the deep comprehension opportunity. Solution: Prepare specific, probing questions; use annotation tools; facilitate peer discussion.

## Integration with UK National Curriculum

### Key Stage 2

While PRIMM was designed primarily for textual programming at secondary level, adapted approaches work at KS2:

- Use Scratch or block-based languages for Predict-Run-Investigate
- Simplify Modify tasks to single-block changes
- Keep Make tasks closely aligned to investigated examples
- Phil Bagge's work demonstrates effective KS2 PRIMM implementation with physical computing (Micro:bit, Crumble)

### Key Stage 3

PRIMM directly supports NC requirements:

- "Use two or more programming languages, at least one of which is textual" – PRIMM works identically across languages, supporting transfer
- "Understand several key algorithms that reflect computational thinking" – Investigation phase makes algorithmic patterns explicit
- "Undertake creative projects" – Make phase enables creative application

### Key Stage 4 (GCSE)

All GCSE specifications require substantial programming competency:

**AQA 8525**: Paper 2 requires programming skills; PRIMM builds confidence for both examined programming questions and the coursework project.

**OCR J277**: Programming Project (20% of qualification) benefits from structured Make phase approaches documented through PRIMM stages.

**Edexcel 1CP2**: On-screen exam includes programming tasks; PRIMM's Investigate phase builds the code-reading skills needed.

**WJEC Eduqas C500QS**: Component 2 (On-screen test) requires rapid code comprehension – directly developed through PRIMM.

### Key Stage 5 (A-Level)

A-Level specifications demand sophisticated programming:

**AQA 7517**: NEA (20% of A-Level) requires substantial programming; PRIMM progression ensures students reach Make phase with genuine understanding.

**OCR H446**: Programming Project and Algorithmic Programming focuses benefit from PRIMM's structured approach to complex algorithms.

**WJEC A680QS**: Programming Techniques examination includes code comprehension and generation – both PRIMM strengths.

## Complementary Pedagogical Approaches

### PRIMM and Pair Programming

PRIMM combines effectively with pair programming (pioneered by Williams and Kessler, 2000, and promoted by Sue Sentance for Computing education). Pairs can collaborate on:

- Predict phase discussions
- Investigate phase annotation
- Modify phase implementation
- Make phase design and coding

### PRIMM and Semantic Waves

Miles Berry and Sue Sentance both discuss the importance of oscillating between concrete and abstract understanding. PRIMM naturally creates this rhythm, but teachers should make it explicit, using meta-cognitive discussion: "We've seen specific examples – what general rule can we extract?"

### PRIMM and Unplugged Activities

Mark Dorling and Phil Bagge emphasise unplugged (computer-free) activities for developing computational thinking. PRIMM's Predict phase works well as an unplugged activity, with students tracing code on paper before computer access.

### PRIMM and Physical Computing

Phil Bagge's work with Raspberry Pi, Micro:bit, and Arduino demonstrates how PRIMM applies to physical computing. The Run phase becomes particularly engaging with tangible outputs (LEDs, motors, sensors), motivating the Predict phase and making Investigate concrete.

## Research Impact and Ongoing Development

Sue Sentance continues to research PRIMM's effectiveness through the Raspberry Pi Foundation's Computing Education Research Centre. Recent findings (2021-2023) indicate:

- Sustained improvement in programming confidence across diverse student populations
- Particular effectiveness for students from backgrounds underrepresented in Computing
- Strong teacher acceptance once initial training is provided
- Adaptability across programming paradigms (procedural, object-oriented, functional)

The National Centre for Computing Education has incorporated PRIMM into its secondary teaching pedagogy courses, training thousands of UK Computing teachers. Simon Peyton Jones, as founding chair of Computing at School, has endorsed PRIMM as evidence-based practice that should become standard in UK Computing education.

## Resources and Further Reading

**Key publications**:
- Sentance, S. & Csizmadia, A. (2017). "Computing in the curriculum: Challenges and strategies from a teacher's perspective." *Education and Information Technologies*, 22(2), 469-495.