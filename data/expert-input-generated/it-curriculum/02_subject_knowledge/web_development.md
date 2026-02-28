# Web Development

## Introduction and Curriculum Context

Web development sits at the intersection of creativity, technical skill and computational thinking within the UK Information Technology and Computer Science curricula. The National Curriculum for Computing (2014) requires pupils to "undertake creative projects that involve selecting, using, and combining multiple applications, preferably across a range of devices" at Key Stage 3, whilst Key Stage 4 and post-16 qualifications explicitly address web technologies as core components of digital literacy and technical competence.

Miles Berry (2014) has emphasised that web development provides an accessible entry point to programming concepts whilst producing tangible, shareable outcomes that motivate learners. His work with Computing at School (CAS) has highlighted how HTML and CSS offer "low floor, high ceiling" opportunities – easy to begin but with substantial depth for extension.

## Key Stage Progression

### Key Stage 2 (Ages 7-11)

Whilst web development is not explicitly mandated at KS2, the National Curriculum requirement that pupils "select, use and combine a variety of software" provides opportunities to introduce basic web concepts. Teachers might introduce:

- Simple HTML structure using platforms like Mozilla Thimble or Glitch
- Understanding that websites comprise multiple interconnected pages
- Basic formatting concepts through visual web editors
- Recognition of URLs, hyperlinks and web architecture

Mark Anderson (ICT Evangelist) has advocated for introducing web concepts through age-appropriate platforms that abstract complexity whilst maintaining authentic web standards, allowing primary pupils to create simple personal pages or class websites.

### Key Stage 3 (Ages 11-14)

The KS3 Computing Programme of Study explicitly requires pupils to "undertake creative projects that involve selecting, using, and combining multiple applications, preferably across a range of devices, to achieve challenging goals." Web development provides an ideal vehicle for this requirement.

Core content should include:

**HTML (Hypertext Markup Language)**
- Semantic structure: headings (h1-h6), paragraphs, lists (ordered and unordered)
- Document structure: DOCTYPE, html, head, body elements
- Hyperlinks and navigation between pages
- Embedding images, audio and video content
- Forms and user input elements
- HTML5 semantic elements (header, nav, article, section, footer)

**CSS (Cascading Style Sheets)**
- Separation of content and presentation
- Selectors: element, class, ID
- Box model: margin, border, padding, content
- Typography: fonts, sizing, line-height, text properties
- Colour theory and application (hex, RGB, HSL)
- Layout techniques: float, positioning, flexbox introduction
- Responsive design principles using media queries
- CSS3 features: transitions, transforms, animations

**Web Architecture and Protocols**
- Client-server model
- HTTP/HTTPS protocols
- Domain Name System (DNS)
- Web hosting concepts
- File and folder structures

Bob Harrison's work on progression in computing education (2018) emphasises that web development should progress from declarative languages (HTML/CSS) to procedural approaches (JavaScript), allowing students to consolidate understanding of syntax and structure before introducing algorithmic complexity.

### Key Stage 4 (Ages 14-16)

GCSE specifications across all major exam boards include web development components:

**AQA GCSE Computer Science (8525)**
Requires understanding of HTML, CSS and JavaScript within the "Fundamentals of programming" section. Students must demonstrate ability to create interactive web content.

**OCR GCSE Computer Science (J277)**
Paper 2 includes web technologies within computational thinking and programming. The Creative iMedia specification (J834) provides extensive web development content including client requirements, design principles and production techniques.

**Edexcel GCSE Computer Science (1CP2)**
Addresses HTML, CSS and JavaScript within programming paradigms, emphasising practical application.

**WJEC GCSE Computer Science**
Includes web technologies within the programming unit, with emphasis on form validation and user interaction.

At this stage, students should master:

**JavaScript Fundamentals**
- Variables, data types and operators
- Control structures: selection (if/else, switch) and iteration (for, while loops)
- Functions and scope
- DOM (Document Object Model) manipulation
- Event handling (click, submit, load events)
- Form validation
- Arrays and objects
- Basic debugging techniques

**Advanced HTML/CSS**
- Accessibility considerations (ARIA labels, semantic HTML)
- CSS Grid layout system
- Advanced responsive design patterns
- CSS preprocessors (introduction to Sass/LESS concepts)
- Performance optimisation

**Web Standards and Best Practice**
- W3C validation
- Cross-browser compatibility
- Mobile-first design approach
- Basic security considerations (XSS, injection attacks)

### Key Stage 5 (Ages 16-18)

A-Level and BTEC qualifications provide substantial depth:

**A-Level Computer Science (AQA 7517, OCR H446, Edexcel 9CP0, WJEC A680QS)**
All specifications require advanced understanding of web technologies, server-side processing, databases and security. Students must demonstrate capability with:

- Advanced JavaScript: AJAX, JSON, asynchronous programming
- Server-side languages (typically PHP, Python or Node.js)
- Database integration (SQL queries, CRUD operations)
- RESTful API concepts
- Authentication and session management
- Security principles: encryption, hashing, secure communications

**BTEC Level 3 IT (Pearson)**
Units such as "Website Development" and "Digital Applications" provide vocational context, requiring students to:

- Conduct client consultations and requirements gathering
- Create design documentation (wireframes, navigation diagrams, mood boards)
- Develop functional websites meeting specified criteria
- Test systematically and document outcomes
- Evaluate effectiveness against user requirements

## Pedagogical Approaches

### Constructionist Learning

Miles Berry's advocacy for constructionist approaches (drawing on Seymour Papert's work) emphasises that web development allows students to create "personally meaningful artefacts." Students should develop websites around topics of genuine interest, promoting engagement and deeper learning.

### Unplugged Activities

Before coding, teachers should employ unplugged activities:
- Physical hyperlink networks using string between paper "pages"
- Card-sorting exercises for information architecture
- Paper prototyping for layout and design
- CSS selector games using physical objects

### Scaffolding and Code Templates

Research by Neil Selwyn (2019) examining technology education highlights the importance of appropriate scaffolding. For web development, this includes:

- Providing HTML/CSS templates that students modify before creating from scratch
- Progressive complexity: start with single-page sites before multi-page projects
- Structured code comments explaining function and purpose
- Exemplar websites demonstrating best practice

### Live Coding and Demonstration

Mark Anderson advocates for regular live coding sessions where teachers demonstrate problem-solving processes, including making deliberate errors and debugging. This demystifies development and models professional practice.

## Technical Infrastructure and Tools

### Development Environments

**Online Platforms**
- Replit (formerly Repl.it): collaborative, browser-based IDE with instant preview
- Glitch: community-focused, excellent for remix culture and sharing
- CodePen: ideal for HTML/CSS/JavaScript experimentation
- JSFiddle: lightweight testing environment

**Desktop Editors**
- Visual Studio Code: professional-grade, excellent extension ecosystem
- Brackets: Adobe's web-focused editor with live preview
- Sublime Text: lightweight, highly customisable
- Notepad++: simple but effective for Windows environments

### Version Control

Introduce Git and GitHub at KS4/5 to mirror professional practice:
- Version history and rollback capabilities
- Collaborative development workflows
- Portfolio development through public repositories
- Introduction to branching and merging concepts

### Testing and Validation

- W3C Markup Validation Service for HTML compliance
- W3C CSS Validation Service
- Browser developer tools (Chrome DevTools, Firefox Developer Tools)
- Lighthouse for performance and accessibility auditing
- Cross-browser testing tools (BrowserStack, CrossBrowserTesting)

## Accessibility and Inclusive Design

The Equality Act 2010 requires consideration of accessibility in digital products. Web development education must address:

- WCAG 2.1 (Web Content Accessibility Guidelines) principles
- Semantic HTML for screen reader compatibility
- Keyboard navigation functionality
- Colour contrast ratios for visual impairment
- Alternative text for images
- ARIA (Accessible Rich Internet Applications) attributes

Miles Berry has emphasised that teaching accessibility early embeds ethical practice and prepares students for professional requirements.

## Security Principles

At KS4 and particularly KS5, introduce fundamental web security concepts:

- Input validation and sanitisation
- SQL injection prevention
- Cross-Site Scripting (XSS) mitigation
- Cross-Site Request Forgery (CSRF) protection
- Password hashing (bcrypt, Argon2)
- HTTPS and SSL/TLS certificates
- Same-origin policy
- Content Security Policy headers

Bob Harrison's work on computational thinking includes security as a fundamental consideration, not an afterthought.

## Assessment Approaches

### Formative Assessment

- Code reviews (peer and teacher)
- Progressive check-ins during project development
- Quick debugging challenges
- "Code golf" exercises (achieving outcomes with minimal code)
- Pair programming observations

### Summative Assessment

**Practical Projects**
All GCSE and A-Level specifications include substantial coursework or practical programming components. Assessment criteria typically address:

- Functionality: does the website work as intended?
- Code quality: readability, efficiency, appropriate commenting
- User experience: interface design, navigation, responsiveness
- Testing: systematic approach, documentation, debugging evidence
- Evaluation: critical reflection on outcomes and process

**Written Examinations**
Questions typically include:
- Code comprehension and annotation
- Error identification and correction
- Completing partially-written code
- Explaining concepts (protocols, standards, security)
- Evaluating design decisions

### Portfolio Development

Neil Selwyn's research (2017) on digital portfolio assessment highlights the value of cumulative web portfolios where students showcase progressive development. This approach:

- Demonstrates growth over time
- Provides authentic audience for work
- Develops professional presentation skills
- Facilitates reflection through project documentation

## Common Misconceptions and Challenges

### "Web Development Isn't Real Programming"

Some educators prioritise "traditional" programming languages over web technologies. However, JavaScript is a fully-featured, Turing-complete language with complex paradigms (functional, object-oriented, event-driven). Miles Berry has argued that this prejudice undermines accessible pathways into computing.

### Over-Reliance on Visual Editors

Whilst WYSIWYG editors (Dreamweaver, Wix, WordPress themes) have pedagogical value for demonstrating concepts, students must engage with underlying code to develop genuine understanding. Bob Harrison emphasises the importance of "looking under the hood."

### Separation of Concerns

Students often embed CSS directly in HTML (inline styles) or mix JavaScript with HTML (onclick attributes). Teaching separation of concerns (HTML for structure, CSS for presentation, JavaScript for behaviour) requires explicit instruction and reinforcement.

### Responsive Design Complexity

Students accustomed to desktop-only development struggle with responsive design principles. Mobile-first approaches should be taught from the outset at KS3.

### Browser Differences

Cross-browser compatibility issues frustrate students. Teaching should acknowledge that web development involves testing across platforms and that vendor prefixes and polyfills are professional necessities.

## Professional Pathways and Industry Relevance

Web development provides clear routes to employment:

- Front-end developer (HTML/CSS/JavaScript frameworks)
- Back-end developer (server-side languages, databases)
- Full-stack developer (both front and back-end)
- UI/UX designer (design principles, prototyping tools)
- Web accessibility specialist
- DevOps engineer (deployment, automation)

The Tech Partnership's "Employer Insights" reports consistently identify web development skills among the most in-demand technical competencies. Connecting classroom practice to professional contexts increases student motivation and career awareness.

## Contemporary Frameworks and Progression

Whilst GCSE and A-Level specifications focus on vanilla HTML, CSS and JavaScript, teachers should be aware of professional frameworks students may encounter:

**JavaScript Frameworks/Libraries**
- React (Facebook): component-based architecture
- Vue.js: progressive framework, accessible for beginners
- Angular (Google): comprehensive framework for large applications
- jQuery: simplified DOM manipulation (declining usage but still prevalent)

**CSS Frameworks**
- Bootstrap: responsive grid system and components
- Tailwind CSS: utility-first approach
- Foundation: responsive front-end framework

**Build Tools and Task Runners**
- Webpack: module bundling
- npm (Node Package Manager): dependency management
- Sass/LESS: CSS preprocessing

Introducing these at KS5 provides authentic technical depth whilst maintaining focus on fundamental concepts.

## Conclusion

Web development in UK Information Technology education provides a uniquely accessible yet technically rigorous domain that addresses National Curriculum requirements whilst connecting to tangible career pathways. As Miles Berry argues, web technologies offer "a way in to computational thinking that feels creative, expressive and personally meaningful" whilst developing transferable skills in problem-solving, design thinking and technical literacy.

Effective pedagogy balances technical skill development with creative expression, industry relevance with educational theory, and practical competence with conceptual understanding. By progressing systematically from declarative markup through styling to imperative programming, educators can build confident, capable web developers equipped for further study or employment in the digital economy.

## Further Reading and Resources

- Berry, M. (2014) "Computing in the National Curriculum: A Guide for Primary Teachers", Computing at School
- Harrison, B. (2018) "Progress in Computing Education", Teaching Computing
- Selwyn, N. (2019) "Should robots replace teachers? AI and the future of education", Polity Press
- Anderson, M. (@ICTEvangelist) - Regularly updated resources and pedagogical approaches
- Computing at School Community: https://www.computingatschool.org.uk/
- Ofsted (2022) "Research review series: computing" - Review of computing education quality
- Royal Society (2017) "After the reboot: computing education in UK schools"