# Data Representation and Binary

## Introduction and Curriculum Context

Data representation is a fundamental concept in Computing education, underpinning understanding of how computers store and process all forms of information. The UK National Curriculum for Computing explicitly requires pupils to "understand how data of various types... can be represented and manipulated digitally, in the form of binary digits" (DfE, 2013). This knowledge forms part of the Computer Science strand and is essential for developing computational thinking.

Simon Peyton Jones, in his influential work on the 2012 Computing curriculum reform, emphasised that understanding binary and data representation helps pupils appreciate that computers are not magic boxes but logical machines that manipulate symbols according to rules. Miles Berry has similarly argued that data representation provides crucial insights into the limitations and capabilities of digital systems.

## Key Stage Progression

### Key Stage 2 (Ages 7-11)

At KS2, the National Curriculum states pupils should "understand computer networks including the internet; how they can provide multiple services, such as the world wide web; and the opportunities they offer for communication and collaboration." Whilst binary is not explicitly mentioned, teachers should introduce foundational concepts:

- Understanding that computers use only two states (on/off, yes/no, 1/0)
- Simple counting in binary using physical representations (cups up/down, lights on/off)
- Recognition that all digital data (text, images, sound) is stored as numbers

Phil Bagge, writing for the Raspberry Pi Foundation, advocates for using unplugged activities at this stage, such as the "Binary Bracelets" activity where children encode their names using binary-coded decimal representations. This concrete approach builds intuitive understanding before formal instruction.

### Key Stage 3 (Ages 11-14)

The KS3 curriculum explicitly requires students to "understand how numbers can be represented in binary, and be able to carry out simple operations on binary numbers." This includes:

- Converting between binary (base 2) and denary (base 10) number systems
- Understanding binary addition and its relationship to logical gates
- Appreciating how binary digits (bits) group into bytes (8 bits)
- Introduction to hexadecimal as a human-readable representation of binary
- Understanding how text is represented using character encoding schemes (ASCII, Unicode)
- Basic understanding of how images are represented using pixels and colour depth
- Introduction to how sound is digitised through sampling

Sue Sentance and colleagues at King's College London have researched effective pedagogies for teaching binary at KS3, finding that students benefit from multiple representations: concrete manipulatives, visual diagrams, and practical programming exercises that convert between number systems.

### Key Stage 4 (Ages 14-16)

GCSE Computer Science specifications from all major exam boards include substantial content on data representation:

**AQA (8525)**: Requires understanding of binary, hexadecimal, character encoding (ASCII and Unicode), representing images (bitmap and vector graphics), representing sound (sample rate, bit depth, bit rate), and data compression.

**OCR (J277)**: Includes binary arithmetic (addition and shifts), hexadecimal, character sets, bitmap images, sound sampling, and compression algorithms.

**Edexcel (1CP2)**: Covers binary and hexadecimal conversions, binary addition, ASCII and Unicode, bitmap images, sound representation, and compression techniques.

**WJEC/Eduqas**: Similar content with emphasis on calculations involving file sizes and storage requirements.

At this level, students must develop fluency in:

- Binary addition with overflow and carry operations
- Binary shifts (multiplication and division by powers of 2)
- Understanding two's complement representation for negative numbers
- Hexadecimal notation and conversion between binary, denary, and hexadecimal
- Detailed knowledge of ASCII (7-bit, 128 characters) vs Unicode (variable-length encoding, supporting international characters)
- Calculating image file sizes: resolution × colour depth
- Understanding colour depth (bit depth) and its impact on image quality
- Calculating sound file sizes: sample rate × bit depth × duration × channels
- Distinguishing between lossy (MP3, JPEG) and lossless (PNG, FLAC) compression

### Key Stage 5 (Ages 16-18)

A-Level Computer Science specifications extend these concepts significantly:

**AQA (7517)**: Includes normalised floating-point representation (mantissa and exponent), bitwise manipulation, and advanced compression algorithms.

**OCR (H446)**: Covers floating-point representation, character encoding in depth, run-length encoding, dictionary-based compression, and error detection/correction.

**Edexcel (9CP0)**: Similar content with additional focus on Boolean algebra and its relationship to binary operations.

A-Level students must understand:

- Floating-point representation using mantissa and exponent
- Precision and rounding errors in floating-point arithmetic
- Advanced compression: run-length encoding (RLE), Huffman coding, Lempel-Ziv-Welch (LZW)
- Error detection and correction: parity bits, checksums, Hamming code
- The trade-offs between compression ratio, quality loss, and computational overhead

## Fundamental Concepts and Common Misconceptions

### Binary Number System

Binary is a base-2 positional number system using only digits 0 and 1. Each position represents a power of 2, reading from right to left: 2⁰ (1), 2¹ (2), 2² (4), 2³ (8), 2⁴ (16), and so forth.

Example: 10110₂ = (1×16) + (0×8) + (1×4) + (1×2) + (0×1) = 22₁₀

**Common misconceptions** identified by Mark Dorling and colleagues at CAS (Computing At School):

1. **Binary as a different type of number**: Students often believe binary numbers are fundamentally different from denary numbers, rather than simply a different notation for the same quantities.

2. **Confusion between bits and bytes**: Many students struggle to distinguish between bit (binary digit) and byte (8 bits), particularly when calculating file sizes.

3. **Hexadecimal understanding**: Students may treat hexadecimal as arbitrary rather than understanding it as base-16, grouping four binary digits for convenience.

### Character Encoding

ASCII (American Standard Code for Information Interchange) uses 7 bits to represent 128 characters, including uppercase and lowercase letters, digits, punctuation, and control characters. Extended ASCII uses 8 bits for 256 characters.

Unicode was developed to represent characters from all writing systems worldwide. UTF-8 (8-bit Unicode Transformation Format) uses 1-4 bytes per character, maintaining backward compatibility with ASCII. UTF-16 uses 2 or 4 bytes, while UTF-32 uses 4 bytes consistently.

**Teaching consideration**: Sue Sentance recommends using practical activities where students examine actual text files in hex editors to see how characters are stored, making abstract concepts tangible.

### Image Representation

Bitmap (raster) images store colour values for each pixel in a grid. Key concepts:

- **Resolution**: Width × height in pixels (e.g., 1920×1080)
- **Colour depth**: Bits per pixel determining colour range (1-bit = 2 colours, 8-bit = 256 colours, 24-bit = 16.7 million colours)
- **File size calculation**: Width × height × colour depth ÷ 8 (for bytes)

Example: A 1920×1080 pixel image with 24-bit colour depth:
1920 × 1080 × 24 = 49,766,400 bits = 6,220,800 bytes ≈ 6.22 MB (uncompressed)

Vector graphics store images as mathematical descriptions of shapes, making them resolution-independent and typically smaller for simple images.

### Sound Representation

Digital sound is created through analogue-to-digital conversion (ADC):

- **Sample rate**: Number of measurements per second (Hz). CD quality is 44,100 Hz (44.1 kHz).
- **Bit depth**: Bits per sample determining amplitude precision (16-bit CD quality, 24-bit studio quality).
- **Bit rate**: Sample rate × bit depth × number of channels (bits per second).

Example: 3-minute CD-quality stereo audio:
44,100 × 16 × 2 × 180 = 254,016,000 bits ≈ 30.48 MB (uncompressed)

**Nyquist-Shannon sampling theorem**: The sample rate must be at least twice the highest frequency in the source audio to accurately reproduce it. This explains why 44.1 kHz sampling can capture human hearing range (20 Hz - 20 kHz).

### Data Compression

**Lossy compression** (JPEG, MP3, MP4): Removes data deemed less important to human perception, achieving high compression ratios but permanently losing information. Uses techniques like:
- Perceptual coding (removing sounds humans cannot easily hear)
- Discrete cosine transforms (for images)
- Temporal compression (storing only changes between video frames)

**Lossless compression** (PNG, ZIP, FLAC): Reduces file size without information loss, using techniques including:
- Run-length encoding: Replacing repeated values with a count and single value (e.g., "AAAAA" becomes "5A")
- Dictionary-based methods: Replacing common patterns with shorter codes
- Huffman coding: Variable-length codes with shorter codes for frequent symbols

Mark Dorling has emphasised that students should understand compression not merely as algorithms but in terms of why it matters: economic costs of storage and transmission, environmental impact of data centres, and user experience considerations.

## Practical Teaching Approaches

### Unplugged Activities

Phil Bagge and the CS Unplugged project (Tim Bell et al.) provide excellent resources:

- **Binary cards/dots**: Using cards with 1, 2, 4, 8, 16, etc. dots to build numbers
- **Human binary counters**: Students stand as bits, sitting/standing for 0/1
- **Sorting networks**: Physical demonstrations of how binary comparison works
- **Image compression**: Using physical materials to demonstrate RLE

### Programming Integration

Miles Berry advocates connecting data representation to practical programming:

- Python bitwise operations (`&`, `|`, `^`, `<<`, `>>`)
- Converting between number bases using built-in functions (`bin()`, `hex()`, `int()`)
- Writing functions to perform conversions manually
- Creating bitmap image files programmatically to understand file formats
- Implementing simple compression algorithms

Example Python activity:
```python
def binary_to_denary(binary_string):
    total = 0
    power = 0
    for digit in reversed(binary_string):
        if digit == '1':
            total += 2 ** power
        power += 1
    return total
```

### Cross-Curricular Links

- **Mathematics**: Number bases connect to place value understanding and powers
- **Science**: Digital sensors and measurement precision
- **Music**: Sound sampling relates to waveforms and frequency
- **Art**: Digital image creation and colour theory
- **Geography**: Satellite imagery resolution and data storage

## Assessment Considerations

### Common Examination Questions

GCSE and A-Level papers typically include:

1. **Conversion questions**: Binary ↔ denary ↔ hexadecimal
2. **Binary arithmetic**: Addition problems with 8-bit numbers
3. **Calculation questions**: Image file sizes, sound file sizes
4. **Comparison questions**: ASCII vs Unicode, lossy vs lossless compression
5. **Explanation questions**: Why use hexadecimal? How does compression work?
6. **Problem-solving**: Given storage capacity, how long can audio recording be?

### Formative Assessment Strategies

Sue Sentance's research on Computing pedagogy suggests:

- **Diagnostic questions**: CAS diagnostic questions database provides tested items
- **Live binary counting**: Quick starter activities to check fluency
- **Peer teaching**: Students explaining conversions to each other reveals understanding gaps
- **Programming challenges**: Convert numbers, create simple image files
- **Think-aloud protocols**: Students verbalise their conversion process

## Links to Other Computing Concepts

### Computer Architecture

Understanding binary directly supports learning about:
- CPU registers storing binary values
- Memory addressing using binary locations
- Machine code and instruction encoding
- Logic gates performing binary operations (AND, OR, NOT, XOR)

Simon Peyton Jones has argued that data representation and computer architecture should be taught in parallel, with each concept reinforcing the other.

### Programming and Algorithms

- Boolean logic and conditional statements
- Bitwise operations for efficient programming
- Data structures storing binary information
- Encoding algorithms (encryption, error correction)

### Networks and Security

- IP addresses as 32-bit (IPv4) or 128-bit (IPv6) binary numbers
- Packet structure and binary protocols
- Encryption operating on binary data
- Data transmission and error checking using parity bits

## Research and Evidence-Based Practice

Sue Sentance and colleagues at King's College London have conducted extensive research on misconceptions in Computing education. Their findings on data representation include:

- Students benefit from seeing the same concept represented in multiple ways (enactive, iconic, symbolic - following Bruner's theory)
- Concrete manipulatives (binary cards, physical bits) significantly improve initial understanding
- Regular low-stakes practice with conversions builds automaticity
- Real-world contexts (social media photo uploads, music streaming) increase engagement

The Raspberry Pi Foundation's research on Computing pedagogy (led by researchers including Phil Bagge) emphasises:

- Starter activities using binary maintain fluency
- Programming tasks that require binary understanding cement knowledge
- Project-based work (creating compressed file formats) motivates deeper learning

## Professional Development Resources

Teachers seeking to strengthen their subject knowledge should consult:

- **Computing At School (CAS)**: Community resources and regional meetings
- **Isaac Computer Science** (isaaccomputerscience.org): Comprehensive A-Level content
- **Craig'n'Dave**: Video tutorials aligned to UK exam specifications
- **Raspberry Pi Foundation**: Free online courses on teaching Computing
- **NCCE (National Centre for Computing Education)**: Face-to-face and remote CPD

Miles Berry's blog (milesberry.net) provides thoughtful commentary on curriculum development and pedagogy. The Computing At School wiki (community.computingatschool.org.uk) contains hundreds of teacher-contributed resources.

## Conclusion

Data representation and binary form the foundational knowledge students need to understand how computers work at a fundamental level. As Mark Dorling has argued, this is not merely technical knowledge but develops logical thinking, precision, and appreciation of how abstract symbols can represent real-world phenomena. Effective teaching combines concrete experiences, procedural practice, conceptual understanding, and practical application through programming, ensuring students develop robust mental models that transfer across the Computing curriculum.