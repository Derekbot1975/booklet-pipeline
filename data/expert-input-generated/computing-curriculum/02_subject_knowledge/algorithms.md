# Algorithms and Data Structures

## Overview and Curriculum Context

Algorithms and data structures form the foundational theoretical and practical underpinning of Computing as a discipline. As Simon Peyton Jones has argued in his work with the Royal Society (2012), computational thinking—of which algorithmic thinking is a core component—represents a fundamental skill comparable to literacy and numeracy in the 21st century. The UK National Curriculum for Computing (2013) explicitly positions "design, use and evaluate computational abstractions that model the state and behaviour of real-world problems and physical systems" as a key stage 3 and 4 requirement, making algorithmic thinking central to statutory provision.

Mark Dorling's work with Computing At School (CAS) has been instrumental in defining progression frameworks that articulate how algorithmic concepts develop from EYFS through to A-level. The CAS Progression Pathways document (2013) provides detailed guidance on how students move from simple sequence understanding in Key Stage 1 to sophisticated analysis of algorithmic efficiency at Key Stage 5.

## Key Stage Breakdown

### Key Stage 1 (Ages 5-7)

At KS1, the National Curriculum requires pupils to "understand what algorithms are; how they are implemented as programs on digital devices; and that programs execute by following precise and unambiguous instructions" and "create and debug simple programs".

**Practical implications for teachers:**
- Focus on concrete, unplugged activities before introducing screen-based programming
- Use everyday contexts: recipes, getting dressed sequences, playground games
- Phil Bagge's work emphasises the importance of physical embodiment—having children 'be the algorithm' by following instructions physically
- Simple data structures emerge implicitly through grouping and sorting activities (toys by colour, shapes by size)

### Key Stage 2 (Ages 7-11)

The curriculum extends to requiring pupils to "design, write and debug programs that accomplish specific goals" and "use sequence, selection, and repetition in programs; work with variables and various forms of input and output".

**Key concepts:**
- **Sequence**: Understanding order and precision in instruction sets
- **Selection**: Introduction to conditional logic (if/then/else statements)
- **Repetition**: Understanding loops (definite and indefinite iteration)
- **Variables**: As named storage locations that can change value

**Data structures at KS2:**
Miles Berry's work on primary computing emphasises introducing simple data structures implicitly through lists and tables. Variables can be understood as single-item storage, whilst lists represent collections. The Scratch programming environment (widely used in UK primaries) provides accessible list structures.

Sue Sentance's research at King's College London (2014-present) through the TPACK framework highlights that primary teachers often lack confidence in computational concepts. Effective CPD should focus on teachers understanding these structures through multiple representations: physical objects, diagrams, and code.

### Key Stage 3 (Ages 11-14)

The KS3 curriculum requires pupils to "use 2 or more programming languages, at least one of which is textual" and "understand simple Boolean logic and its use in controlling program flow".

**Algorithmic concepts:**
- **Decomposition**: Breaking problems into manageable sub-problems
- **Pattern recognition**: Identifying similarities and commonalities
- **Abstraction**: Removing unnecessary detail to focus on core features
- **Algorithm design**: Creating step-by-step solutions before coding
- **Boolean logic**: AND, OR, NOT operations and truth tables

**Data structures:**
- **Arrays/Lists**: Understanding indexed collections
- **Records/Dictionaries**: Key-value pair structures
- **Two-dimensional data structures**: Tables, grids, matrices

**Searching and sorting:**
Introduction to linear search and simple sorting algorithms (bubble sort, insertion sort) provides concrete contexts for understanding algorithmic efficiency, though formal complexity analysis is typically reserved for KS4/5.

Mark Dorling's QuickStart Computing resources emphasise computational thinking unplugged activities at KS3, including card-sorting exercises that physically demonstrate sorting algorithms, making abstract concepts tangible.

### Key Stage 4 (GCSE, Ages 14-16)

All major exam boards (AQA, Edexcel/Pearson, OCR, WJEC/Eduqas) include substantial coverage of algorithms and data structures in their GCSE Computer Science specifications.

**Common algorithmic requirements across boards:**

**Searching algorithms:**
- Linear (sequential) search
- Binary search (including prerequisite that data must be ordered)
- Comparative analysis of efficiency

**Sorting algorithms:**
- Bubble sort
- Merge sort
- Insertion sort
- Understanding trade-offs between simplicity and efficiency

**Standard algorithms:**
- Finding maximum/minimum values
- Counting occurrences
- Totalling/averaging values
- Validation and verification routines

**Data structures (all boards):**
- **Arrays** (one and two-dimensional)
- **Records/structures** (composite data types)
- **Files** (sequential file handling)

**OCR specification additionally includes:**
- Stacks (LIFO structures) with push, pop, peek operations
- Queues (FIFO structures) with enqueue, dequeue operations
- Linked lists, trees, and graphs at a conceptual level

**AQA specification emphasises:**
- Practical application through the programming project (non-exam assessment)
- Use of sub-programs (procedures and functions) as algorithmic building blocks
- SQL for database operations as a declarative algorithmic approach

**Algorithm representation:**
All boards require understanding of multiple representation methods:
- Flowcharts (using standard ISO 5807 symbols)
- Pseudocode (each board provides its own formal syntax)
- Structured English
- Working code in a high-level language (typically Python)

### Key Stage 5 (A-level, Ages 16-18)

A-level specifications represent a significant step up in theoretical depth and mathematical rigour.

**AQA A-level Computer Science:**

**Algorithmic complexity:**
- Big O notation for time complexity
- Analysis of O(1), O(n), O(n²), O(n log n), O(2ⁿ) classifications
- Space complexity considerations
- Best, average, and worst-case scenarios

**Advanced searching/sorting:**
- Detailed analysis of QuickSort and MergeSort
- Understanding recursive algorithm design
- Practical implementation and efficiency testing

**Data structures:**
- **Static vs dynamic structures**
- **Stacks** with applications (function call stack, expression evaluation, backtracking)
- **Queues** including priority queues and circular queues
- **Graphs** (adjacency matrix and adjacency list representations)
- **Trees**: binary trees, binary search trees, tree traversal (in-order, pre-order, post-order)
- **Hash tables** with collision resolution strategies

**OCR A-level (H446):**
Similar coverage with additional emphasis on:
- **Recursion** as a problem-solving technique (base cases, recursive cases)
- Linked lists with detailed implementation understanding
- Graph algorithms including Dijkstra's shortest path algorithm
- Role of the operating system in memory management for data structures

**Edexcel/Pearson:**
Distinctive elements include:
- Vector and matrix representations for games and graphics
- Practical project requiring sophisticated data structure selection

## Pedagogical Approaches and Research Evidence

### The Importance of Multiple Representations

Sue Sentance's research with the ScratchMaths project and subsequent work at King's College London demonstrates that students develop deeper understanding when concepts are presented through multiple modalities. For algorithms and data structures, this means:

1. **Unplugged activities** (no computers) to introduce concepts physically
2. **Visual representations** through tools like Python Tutor or VisuAlgo
3. **Pseudocode** for language-independent expression
4. **Working code** in actual programming languages
5. **Written explanations** requiring articulation of understanding

### Common Misconceptions

Research by the National Centre for Computing Education (NCCE) identifies persistent misconceptions:

**Variables and assignment:**
- Believing `=` represents mathematical equality rather than assignment
- Not understanding that variable names are arbitrary labels
- Confusion about variable scope

**Iteration:**
- Difficulty predicting how many times loops execute
- Confusion between count-controlled and condition-controlled loops
- Off-by-one errors in array indexing

**Algorithms and efficiency:**
- Believing 'efficiency' only means 'speed'
- Not recognising that algorithm choice depends on context (data size, data characteristics)
- Difficulty translating algorithm understanding into code

### Effective Teaching Strategies

**1. Concrete-Pictorial-Abstract (CPA) progression:**
Phil Bagge's work demonstrates effectiveness of starting with physical manipulatives (cards to sort, cups to stack), moving to diagrams, then abstract code.

**2. Worked examples and completion problems:**
Rather than always building from scratch, providing partial solutions with gaps develops understanding efficiently. Research by Atkinson et al. (2000), applied to computing education by Sentance, shows this reduces cognitive load.

**3. Tracing and prediction:**
Before writing algorithms, students should practice tracing existing code with pencil and paper, predicting outputs. This develops the mental models necessary for code construction.

**4. Live coding with commentary:**
Teacher demonstration where thinking is verbalised ("I'm using a for loop here because I know exactly how many times to iterate...") makes expert thinking visible.

**5. Peer instruction:**
Students explain algorithmic solutions to peers, teaching being an effective learning mechanism.

## Assessment Considerations

### Formative Assessment Strategies

**Diagnostic questions:**
The NCCE Isaac Computer Science platform (developed with involvement from Cambridge academics including Simon Peyton Jones) provides targeted diagnostic questions that reveal specific misconceptions about algorithms and data structures.

**Code tracing exercises:**
Regular practice predicting program output develops accuracy and reveals gaps in understanding loop mechanics, variable state, and data structure behaviour.

**Design before implementation:**
Requiring algorithm design (flowchart or pseudocode) before coding encourages planning and reveals whether students understand the logical structure independent of syntax.

### Summative Assessment (GCSE)

All exam boards assess through:

**Paper-based questions requiring:**
- Completing partially written algorithms
- Identifying errors in given code
- Explaining algorithm operation through trace tables
- Comparing algorithmic approaches
- Writing algorithms in pseudocode or programming language

**Programming project (non-exam assessment):**
Typically 20% of GCSE, requiring selection and implementation of appropriate data structures and algorithms for a substantial problem. Documented design showing algorithmic planning is specifically assessed.

### A-level Assessment

**AQA and OCR include:**
- Extended response questions requiring detailed explanations of data structure choice
- Algorithm efficiency analysis using Big O notation
- Implementation tasks in specific programming languages
- Substantial programming project (NEA - Non-Exam Assessment) worth 20%

## Progression and Curriculum Sequencing

The CAS Progression Pathways framework, refined through Mark Dorling's leadership, suggests careful sequencing:

**Years 1-2:** Sequence understanding through concrete activities
**Years 3-4:** Introduction of selection and repetition with visual programming
**Years 5-6:** Multiple loops, variables, and simple list structures
**Years 7-8:** Text-based programming, systematic algorithm design, Boolean logic
**Year 9:** Standard algorithms, efficiency comparisons, multiple data structures
**Years 10-11:** Formal algorithmic analysis, sophisticated data structure selection
**Years 12-13:** Theoretical computer science, complexity theory, advanced structures

## Tools and Resources

### Programming Environments

**Primary (KS1-2):**
- **Scratch** (MIT): Block-based, accessible, supports lists
- **ScratchJr** (tablets): Even younger learners
- **Logo/Turtle graphics**: Procedural thinking

**Secondary (KS3-5):**
- **Python**: Now dominant in UK schools due to readability and industry relevance
- **Java**: Still used by some schools, particularly for A-level
- **C#/Visual Basic**: Legacy usage declining
- **Online IDEs**: Replit, Trinket allow browser-based coding

### Visualisation Tools

- **Python Tutor** (pythontutor.com): Step-through code execution with stack/heap visualisation
- **VisuAlgo**: Animated algorithms and data structures
- **Sorting algorithm animations**: Multiple available online for comparison

### Professional Resources

- **NCCE (National Centre for Computing Education)**: Free CPD courses including "Programming: Algorithms" and "Programming: Data Structures"
- **Isaac Computer Science**: Comprehensive tutorials and practice questions aligned to UK curricula
- **Computing At School**: Community resources and regional hubs
- **OCR Cambridge**: Programming frameworks and exemplar code

## Links to Computational Thinking

Simon Peyton Jones's advocacy emphasises that algorithms represent *computational thinking made concrete*. The four cornerstones identified by Jeannette Wing (2006) and adopted by CAS directly relate:

1. **Decomposition**: Breaking problems into sub-algorithms (procedures/functions)
2. **Pattern recognition**: Identifying when standard algorithms apply (sorting, searching)
3. **Abstraction**: Data structures as abstract models of information
4. **Algorithm design**: Creating executable solutions

Miles Berry's work highlights that these thinking skills transfer beyond Computing, developing problem-solving capabilities applicable across the curriculum and in everyday life.

## Connection to Wider Computer Science

Understanding algorithms and data structures provides foundation for:

- **Software engineering**: Design patterns and architectural decisions
- **Artificial intelligence**: Search algorithms, decision trees, neural network structures
- **Databases**: Indexing strategies, query optimisation
- **Networks**: Routing algorithms, packet switching
- **Cybersecurity**: Encryption algorithms, hash functions

As Sue Sentance notes in her research on teacher professional development, teachers who understand these connections can make Computing more engaging by showing authentic applications rather than presenting algorithms as abstract exercises.

## Equity and Inclusion Considerations

Research by the Roehampton Annual Computing Education Report (TRACER) and UCL's work on computing participation reveals concerning patterns in who succeeds with algorithmic thinking. Phil Bagge's emphasis on concrete, playful approaches at primary level helps ensure all students, regardless of background, develop foundational understanding before abstract concepts are introduced.

**Strategies for inclusion:**
- Avoid assuming prior programming experience
- Use contexts relevant to diverse student backgrounds
- Recognise that algorithmic thinking develops at different rates
- Provide scaffolding and worked examples for all learners
- Value multiple solution approaches (not assuming one 'correct' algorithm)

## Contemporary Developments

The rapid advancement of artificial intelligence raises questions about what algorithmic knowledge remains essential. However, as Simon Peyton Jones argues, understanding *how* algorithms work becomes *more* important when AI systems make algorithm-driven decisions affecting society. Students who understand algorithmic bias, efficiency trade-offs, and data structure limitations can critically evaluate technological systems rather than being passive users.

The NCCE's curriculum materials (2020-present) increasingly emphasise connections between foundational algorithms (sorting, searching) and machine learning applications (classification, clustering), showing continuity rather than obsolescence of classical computer science knowledge.