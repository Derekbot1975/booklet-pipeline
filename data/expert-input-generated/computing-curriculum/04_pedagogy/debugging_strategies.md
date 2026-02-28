# Teaching Debugging Strategies

## Introduction

Debugging is a fundamental skill within computational thinking and programming that enables learners to identify, analyse and resolve errors in their code. The UK National Curriculum for Computing explicitly requires students to "use logical reasoning to detect and correct errors in algorithms and programs" across all key stages. Sue Sentance and her colleagues at King's College London have emphasised that debugging is not merely about fixing errors, but represents a crucial metacognitive process that develops problem-solving skills and deepens understanding of program execution.

## Theoretical Foundations

### The Nature of Programming Errors

Research by Mark Dorling and others has categorised programming errors into three primary types that students encounter:

**Syntax Errors**: Violations of the programming language's grammatical rules. These are typically caught by compilers or interpreters and are often the first errors novice programmers encounter.

**Runtime Errors**: Errors that occur during program execution, such as division by zero or attempting to access non-existent array indices. These require understanding of program state and data flow.

**Logic Errors**: The most challenging category, where programs execute without error messages but produce incorrect results. Phil Bagge has noted that these errors require the deepest level of computational thinking to identify and resolve.

### Debugging as a Cognitive Process

Simon Peyton Jones, in his work on computing education, has highlighted that debugging requires multiple cognitive skills: reading and comprehending code, forming mental models of program execution, hypothesis formation and testing, and systematic reasoning. Miles Berry's research emphasises that effective debugging strategies must be explicitly taught rather than assumed to develop naturally through programming practice.

## Key Stage Progression

### Key Stage 1 (Ages 5-7)

At KS1, the National Curriculum requires pupils to "understand what algorithms are" and "create and debug simple programs". Debugging at this stage focuses on:

**Visual and Physical Debugging**: Using unplugged activities and floor robots (such as Bee-Bots) where errors in sequences are immediately visible. Teachers should encourage pupils to predict outcomes before execution, then identify discrepancies between predicted and actual behaviour.

**Paired Debugging**: Implementing pair programming approaches where one pupil 'drives' whilst another observes and spots errors. This collaborative approach, advocated by Phil Bagge, develops communication skills alongside debugging capabilities.

**Error Vocabulary**: Introducing age-appropriate language such as "it didn't work", "something went wrong", and "let's try again", building towards more precise terminology like "mistake" and "fix".

### Key Stage 2 (Ages 7-11)

KS2 requirements state pupils should "use logical reasoning to explain how some simple algorithms work and to detect and correct errors in algorithms and programs". This represents a significant development in sophistication:

**Trace Tables and Dry Running**: Introducing systematic approaches to following program flow. Phil Bagge recommends using physical trace tables where pupils manually record variable values at each step of execution. This technique, whilst time-intensive, builds crucial understanding of program state.

**Planned vs Actual Outcomes**: Teaching pupils to articulate what their program should do before testing it. Sue Sentance's research shows that novice programmers often skip this critical step, making it impossible to identify logic errors systematically.

**Decomposition in Debugging**: Breaking programs into smaller sections to isolate where errors occur. Mark Dorling's work on computational thinking emphasises that decomposition is as crucial for debugging as it is for initial program design.

**Print Statement Debugging**: Teaching the strategic use of output statements to inspect variable values and program flow. This remains one of the most practical debugging techniques even for professional programmers.

### Key Stage 3 (Ages 11-14)

The KS3 Programme of Study requires students to "use two or more programming languages, at least one of which is textual" and to "understand simple Boolean logic". Debugging strategies must evolve accordingly:

**Systematic Testing Strategies**: Introducing concepts of test cases, boundary conditions and normal/extreme/erroneous data. The National Centre for Computing Education (NCCE) resources, influenced by Sue Sentance's research, provide structured frameworks for test case development.

**Breakpoints and Step-Through Debugging**: Teaching pupils to use IDE debugging tools such as those in IDLE (Python), Mu Editor, or Scratch's turbo mode. Miles Berry has noted that many teachers avoid teaching these tools due to unfamiliarity, but they provide crucial insight into program execution.

**Rubber Duck Debugging**: Introducing the technique of explaining code line-by-line to an inanimate object (or peer). This metacognitive strategy, whilst appearing trivial, forces systematic code review and often reveals logic errors.

**Version Control Principles**: Teaching pupils to save working versions before making changes, enabling them to revert when debugging introduces new errors. This practice, whilst more commonly associated with software engineering, develops important strategic thinking.

### Key Stage 4 and 5 (Ages 14-18)

GCSE and A-Level specifications from all major exam boards (AQA, OCR, Edexcel, WJEC) explicitly assess debugging skills. The AQA GCSE specification, for instance, requires students to "identify and correct errors in algorithms" and OCR requires understanding of "testing and validation".

**Debugging as Analysis**: At this level, debugging extends beyond fixing errors to analysing why errors occurred and how to prevent similar errors. Sue Sentance's research with post-16 students shows this reflective practice significantly improves code quality.

**Exception Handling**: Teaching explicit error handling mechanisms (try-except blocks in Python, validation in procedural languages). All A-Level specifications include error handling as assessable content.

**Defensive Programming**: Introducing concepts of input validation, type checking, and assertion statements as preventative debugging measures. Simon Peyton Jones has argued that teaching "programming by contract" principles improves student understanding of program correctness.

**Debugging Complex Programs**: Working with multi-file projects, libraries, and API integration where errors may originate outside student-written code. This requires teaching skills in reading documentation, interpreting error messages, and using stack traces effectively.

## Pedagogical Approaches

### Modelling Debugging Processes

Research by the NCCE emphasises the importance of teachers explicitly modelling debugging strategies rather than simply fixing students' code. This involves:

**Think-Aloud Protocol**: Verbalising the debugging thought process: "I notice the loop isn't executing, so I'll check the loop condition" or "The output is wrong, so I'll trace these variables through the calculation". Phil Bagge's classroom videos demonstrate this approach effectively.

**Deliberately Introduced Errors**: Creating programs with known bugs for pupils to find and fix. The NCCE Isaac Computer Science platform includes extensive "debug this code" exercises. These should progress from obvious syntax errors to subtle logic errors.

**Error Analysis Sessions**: Spending lesson time analysing common errors from the class's work (anonymised). Mark Dorling suggests maintaining an "error gallery" that the class builds throughout a unit of work.

### The PRIMM Approach

Developed by Sue Sentance and colleagues, PRIMM (Predict, Run, Investigate, Modify, Make) provides a structured framework that naturally incorporates debugging:

**Predict Phase**: Students predict program behaviour, establishing expectations against which to identify errors.

**Run Phase**: Comparing actual behaviour with predictions, identifying discrepancies that indicate bugs.

**Investigate Phase**: Explicitly analysing why errors occurred and understanding the correct behaviour.

This framework appears in resources from all major UK computing education organisations and aligns with National Curriculum requirements for logical reasoning.

### Teaching Error Message Interpretation

A significant barrier identified by Miles Berry and others is that novice programmers often cannot interpret error messages effectively. Explicit teaching should include:

**Error Message Anatomy**: Teaching students to identify the line number, error type, and error description within messages. Creating classroom displays showing common Python errors (SyntaxError, NameError, TypeError, etc.) with explanations.

**Search Skills**: Teaching effective strategies for searching error messages online, including which parts of error messages to include in searches and how to evaluate search results. This digital literacy aspect is often overlooked but crucial for independent debugging.

**Building Error Libraries**: Encouraging students to maintain personal records of errors encountered and their solutions, developing metacognitive awareness of their common error patterns.

## Practical Classroom Strategies

### Structured Debugging Protocols

Research-informed approaches include:

**The Five-Step Debugging Protocol**:
1. Describe what the program should do
2. Describe what it actually does
3. Identify where in the code the discrepancy occurs
4. Form a hypothesis about the cause
5. Test the hypothesis with a specific fix

This protocol, advocated by the NCCE, makes implicit debugging processes explicit and teachable.

### Debugging Before Creation

Phil Bagge recommends "debugging-first" activities where students work with existing code before writing their own. This develops code reading skills and debugging confidence before the cognitive load of code creation is added. The Raspberry Pi Foundation's Code Club resources include numerous debugging-first projects.

### Peer Debugging and Code Review

Implementing structured peer debugging sessions where students swap programs and provide written feedback using specific frameworks. The AQA GCSE specification includes code tracing questions that can be adapted for peer assessment activities.

### Strategic Use of Development Environments

Different IDEs offer varying support for debugging. Teachers should consider:

**Block-Based Environments** (Scratch, Blockly): Built-in visual execution feedback and immediate error prevention through syntax constraints. Useful for KS1-3.

**Simplified Text Editors** (Mu, Trinket): Provide clear error messages and simplified interfaces suitable for transitioning from block-based to text-based programming.

**Professional IDEs** (PyCharm, Visual Studio Code): Offer comprehensive debugging tools (breakpoints, variable inspection, stack traces) essential for KS4-5 but require explicit teaching to use effectively.

## Assessment Approaches

### Formative Assessment

Sue Sentance's research emphasises that debugging provides rich formative assessment opportunities:

**Error Classification Tasks**: Asking students to categorise errors (syntax, runtime, logic) develops their analytical framework for debugging.

**Trace Table Completion**: Regular low-stakes testing of program tracing skills. All exam boards include trace table questions in their GCSE assessments.

**Debugging Journals**: Students record bugs encountered, hypotheses formed, and solutions implemented. This metacognitive reflection, reviewed regularly, provides insight into developing understanding.

### Summative Assessment

All UK exam boards assess debugging directly:

**AQA GCSE Computer Science**: Paper 2 includes questions requiring students to identify and correct errors in provided code.

**OCR GCSE Computer Science**: J277 specification includes "debugging and testing" as explicit assessment criteria in the programming project.

**Edexcel GCSE Computer Science**: Requires students to "identify and correct errors" in pseudocode and program code.

**A-Level Specifications**: All boards include more complex debugging scenarios, often involving multiple related errors or errors in unfamiliar contexts.

## Common Challenges and Misconceptions

### The "Trial and Error" Trap

Research by Mark Dorling identifies that weak programmers often engage in random code modification without systematic analysis. Teachers must actively discourage this by requiring students to articulate their hypothesis before making changes and insisting on explanation of why changes did or didn't work.

### The "It Doesn't Work" Problem

Students often report that code "doesn't work" without specific analysis. Miles Berry recommends teaching precise error description as a key skill: "What did you expect to happen? What actually happened? When does this occur?"

### Over-Reliance on Teacher Intervention

Phil Bagge notes that students frequently seek teacher help before attempting systematic debugging themselves. Implementing "three before me" policies (try three things before asking the teacher) and providing debugging checklists scaffolds independent problem-solving.

### Syntax Obsession

Novice programmers may focus exclusively on fixing syntax errors whilst ignoring more fundamental logic errors. Teaching the hierarchy of error types and their relative significance helps students prioritise debugging efforts effectively.

## Research Evidence and Recommendations

Sue Sentance's longitudinal research at King's College London demonstrates that explicit teaching of debugging strategies significantly improves programming performance and reduces student frustration. Key evidence-based recommendations include:

1. **Integrate debugging from the first lesson**: Don't wait until students have written substantial code before introducing debugging concepts.

2. **Model expert debugging behaviour**: Regular teacher demonstration of debugging processes develops students' mental models of effective debugging.

3. **Teach preventative strategies alongside reactive debugging**: Input validation, meaningful variable names, and code structure reduce debugging burden.

4. **Provide graduated complexity**: Progress from obvious errors in short programs to subtle errors in complex programs systematically.

5. **Emphasise reading over writing**: Research shows that code comprehension precedes and enables both creation and debugging.

Simon Peyton Jones's work emphasises that debugging teaches broader transferable skills: systematic problem-solving, hypothesis testing, and resilience in the face of failure. These connections should be made explicit to students, particularly when debugging feels frustrating.

## Resources and Further Development

The National Centre for Computing Education provides extensive CPD materials on teaching debugging, including the "Teaching Programming" course developed by Sue Sentance and colleagues. The Isaac Computer Science platform includes debugging exercises aligned with exam specifications.

Teacher subject knowledge development should include experience with professional debugging tools and practices. Phil Bagge's "Code-It" resources and the Raspberry Pi Foundation's teaching materials provide classroom-ready debugging activities across all key stages.

Mark Dorling's work with Computing At School (CAS) has produced the "Computational Thinking Framework" which positions debugging within the broader computational thinking context, helping teachers understand how debugging skills connect to other aspects of the computing curriculum.

## Conclusion

Teaching debugging strategies effectively requires moving beyond simply helping students fix individual errors towards developing systematic problem-solving approaches and metacognitive awareness. The UK National Curriculum's emphasis on logical reasoning provides the framework, whilst research from Sue Sentance, Phil Bagge, Miles Berry and others provides evidence-based pedagogical approaches. By explicitly teaching debugging as a core skill from KS1 through to A-Level, teachers develop not only programming competence but also broader analytical and problem-solving capabilities that serve students across the curriculum and beyond.