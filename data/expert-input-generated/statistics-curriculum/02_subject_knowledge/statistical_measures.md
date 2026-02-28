# Statistical Measures (Averages, Spread, Correlation)

## Overview and Curriculum Context

Statistical measures form the cornerstone of data analysis in the UK mathematics and statistics curriculum. The National Curriculum for England (2014) positions these concepts progressively from Key Stage 2 through to Key Stage 4, with further development at A-level. David Spiegelhalter, Winton Professor of the Public Understanding of Risk at Cambridge, emphasises that understanding measures of central tendency, variation, and association is fundamental to statistical literacy and critical thinking in modern society.

The curriculum distinguishes between descriptive statistics (summarising data) and inferential statistics (drawing conclusions), with measures of averages, spread, and correlation serving primarily descriptive purposes at secondary level, before becoming tools for inference at A-level.

## Measures of Central Tendency (Averages)

### The Three Primary Averages

The UK curriculum introduces three measures of central tendency, each serving distinct purposes:

**Mean (arithmetic average)**: The sum of all values divided by the number of values. Introduced in Key Stage 2 and developed throughout secondary education.

**Median**: The middle value when data is ordered. More resistant to outliers than the mean.

**Mode**: The most frequently occurring value. Particularly relevant for categorical data.

Anne Watson's research on mathematical reasoning highlights that students often struggle to understand why multiple definitions of "average" exist. Teachers must explicitly address this conceptual challenge, helping students recognise that different contexts demand different measures.

### Curriculum Progression

**Key Stage 2**: Children calculate the mean (including decimal quantities) and understand the mode as the most common value.

**Key Stage 3**: The National Curriculum specifies that students should "describe, interpret and compare observed distributions of a single variable through appropriate graphical representation involving discrete, continuous and grouped data; and appropriate measures of central tendency (mean, mode, median)."

**Key Stage 4**: Students work with frequency tables, including grouped data, to estimate means. They compare distributions using measures of central tendency. Foundation tier focuses on straightforward calculations; Higher tier introduces weighted means and choosing appropriate averages for specific contexts.

**A-level (AS/A2)**: Statistical distributions are formalised. AQA, Edexcel, OCR, and WJEC specifications all require calculation of means from frequency distributions and understanding when each measure is appropriate.

### Pedagogical Considerations

Malcolm Swan's work on *Improving Learning in Mathematics* (2005) demonstrates that students benefit from comparing different datasets using multiple measures simultaneously. His diagnostic teaching materials encourage discussion about which average is "best" for different scenarios—a crucial statistical thinking skill.

Adrian Sherratt's contributions to A-level statistics pedagogy emphasise that teachers should move beyond procedural calculation to develop conceptual understanding. For example, students should explore:

- How the mean is influenced by extreme values (outliers)
- Why median household income is typically reported rather than mean income
- When mode is the only appropriate measure (e.g., shoe sizes, favourite colours)

### Common Misconceptions

Research identifies persistent misconceptions:

1. **The mean as the most important average**: Students often treat the mean as the "correct" answer without considering context.
2. **Confusing mode with median**: Particularly when data is already ordered.
3. **Inability to calculate mean from grouped data**: Students struggle with using midpoints as estimates.

## Measures of Spread (Dispersion)

### Range and Interquartile Range

**Range**: The difference between the highest and lowest values. Simple but heavily influenced by outliers.

**Interquartile Range (IQR)**: The difference between the upper quartile (Q3) and lower quartile (Q1), representing the spread of the middle 50% of data.

The National Curriculum for Key Stage 3 requires students to "describe simple mathematical relationships between two variables (bivariate data) in observational and experimental contexts and illustrate using scatter graphs." By Key Stage 4, students must calculate and interpret quartiles, and understand the IQR as a measure of spread.

### Standard Deviation

Standard deviation measures the average distance of data points from the mean. It is introduced at GCSE Higher tier and becomes central at A-level.

**Key Stage 4 (Higher tier)**: Students should understand standard deviation conceptually and use technology to calculate it. AQA's GCSE specification states students must "know that the standard deviation is a measure of spread and be able to use it to compare distributions."

**A-level**: All exam boards require calculation of standard deviation from raw data and frequency tables, using both formulae:

- Standard deviation = √(Σ(x - x̄)² / n)
- Computational formula: √((Σx²/n) - x̄²)

David Spiegelhalter's public engagement work emphasises that standard deviation is crucial for understanding risk and uncertainty. His book *The Art of Statistics* (2019) provides accessible explanations that teachers can adapt for classroom use.

### Variance

Variance (σ²) is the square of standard deviation. While less intuitive than standard deviation, it has important mathematical properties, particularly in inferential statistics at A-level.

### Pedagogical Approaches

Anne Watson's research on conceptual understanding suggests that students need multiple representations:

- **Visual**: Box plots and cumulative frequency curves to display IQR
- **Numerical**: Calculating measures explicitly
- **Contextual**: Interpreting spread in real-world scenarios (e.g., consistency of product quality, reliability of transport services)

Malcolm Swan's teaching materials include activities where students match datasets to their statistical measures, requiring them to reason about relationships between spread and data characteristics.

## Comparing Distributions

### The Mean-Spread Pairing

The National Curriculum emphasises that students should use combinations of measures to compare distributions. The standard approach:

- **Mean with standard deviation** (or range): For symmetrical distributions
- **Median with IQR**: For skewed distributions or data with outliers

This pairing is explicit in all GCSE exam board specifications. Edexcel's Higher tier specification states: "Compare distributions using measures of average and spread."

### Box Plots and Five-Number Summary

Box plots (box-and-whisker diagrams) provide visual comparison using:
- Minimum value
- Lower quartile (Q1)
- Median (Q2)
- Upper quartile (Q3)
- Maximum value

This five-number summary is required at GCSE and A-level. OCR's specification particularly emphasises interpretation and comparison of box plots.

### Outliers

Outliers are typically defined as values falling below Q1 - 1.5×IQR or above Q3 + 1.5×IQR. A-level specifications (particularly Edexcel and AQA) require students to identify and discuss outliers.

David Spiegelhalter's work on data journalism highlights the importance of investigating outliers rather than automatically excluding them—they often contain valuable information.

## Correlation and Scatter Diagrams

### Understanding Correlation

Correlation measures the strength and direction of linear association between two variables. The National Curriculum introduces bivariate data at Key Stage 3, with formal correlation measures at Key Stage 4 (Higher tier) and A-level.

**Positive correlation**: As one variable increases, the other tends to increase.
**Negative correlation**: As one variable increases, the other tends to decrease.
**No correlation**: No linear relationship evident.

### Scatter Diagrams

GCSE specifications (all exam boards) require students to:
- Draw scatter diagrams for bivariate data
- Describe correlation (positive, negative, none)
- Describe strength (strong, moderate, weak)
- Identify outliers
- Draw and use lines of best fit by eye (Foundation and Higher)

### Product Moment Correlation Coefficient (PMCC)

Pearson's product moment correlation coefficient (r) quantifies linear correlation, ranging from -1 to +1. This is an A-level topic across all exam boards.

Key properties:
- r = 1: perfect positive linear correlation
- r = -1: perfect negative linear correlation
- r = 0: no linear correlation
- |r| > 0.75 typically indicates strong correlation
- |r| < 0.25 typically indicates weak correlation

The formula r = Σ(x - x̄)(y - ȳ) / √(Σ(x - x̄)²Σ(y - ȳ)²) is required knowledge, though students typically use calculators for computation.

### Spearman's Rank Correlation Coefficient

Some A-level specifications (notably OCR MEI) include Spearman's rank correlation coefficient (rs) for ordinal data or when data is not linearly related. This non-parametric measure is calculated from ranks rather than raw values.

### Correlation vs Causation

A critical statistical concept emphasised by all UK specifications is that **correlation does not imply causation**. Malcolm Swan's problem-solving materials include activities where students identify spurious correlations and distinguish between:

- **Causal relationships**: X causes Y
- **Common cause**: Z causes both X and Y
- **Coincidental correlation**: No genuine relationship
- **Reverse causation**: Y actually causes X

David Spiegelhalter frequently discusses this in his public communication work, providing examples like the correlation between ice cream sales and drowning deaths (both caused by hot weather).

### Regression and Lines of Best Fit

**GCSE**: Students draw lines of best fit by eye through scatter diagrams to make predictions (interpolation and extrapolation). They should understand limitations of extrapolation.

**A-level**: Formal least squares regression is introduced. The equation of the regression line of y on x takes the form:
y = a + bx, where b = Σ(x - x̄)(y - ȳ) / Σ(x - x̄)² and a = ȳ - bx̄

Students must understand:
- The regression line passes through (x̄, ȳ)
- The line of y on x differs from x on y
- Regression should only be used for prediction when correlation is strong
- The dangers of extrapolation beyond the data range

## Assessment and Examination Approach

### GCSE Level

All major exam boards (AQA, Edexcel, OCR, WJEC) assess statistical measures through:

**Foundation tier**:
- Calculating mean, median, mode, and range from lists and frequency tables
- Interpreting averages and range
- Drawing and interpreting scatter diagrams
- Basic comparison of distributions

**Higher tier**:
- All Foundation content plus:
- Calculating mean from grouped data using midpoints
- Quartiles and interquartile range
- Understanding standard deviation (calculation often via calculator)
- Comparing distributions using appropriate measure pairs
- Lines of best fit and correlation description
- Identifying outliers

### A-level

Statistics appears in A-level Mathematics (typically in the Statistics components) and Further Mathematics. Common assessment areas:

- Calculating all measures from various data presentations
- Choosing appropriate measures with justification
- Coding and scaling problems (e.g., if y = 3x + 5, how does ȳ relate to x̄?)
- Formal hypothesis testing using correlation coefficients
- Regression analysis and prediction with critical evaluation
- Interpretation in context, particularly communicating statistical findings

Edexcel's A-level specification particularly emphasises data cleaning and the impact of outliers. AQA includes questions requiring extended writing about statistical methods.

## Practical Teaching Strategies

### Using Real Data

Adrian Sherratt advocates strongly for using authentic data in teaching statistics. Resources include:

- ONS (Office for National Statistics) data sets
- Censusatschool.org.uk (collaborative data collection project)
- CODAP (Common Online Data Analysis Platform)
- Real sports statistics, climate data, or economic indicators

David Spiegelhalter's *Understanding Uncertainty* website provides contextualised examples appropriate for secondary students.

### Technology Integration

Modern statistics teaching should incorporate:

- **Spreadsheets** (Excel, Google Sheets): Calculating measures, creating visualisations
- **Statistical software** (Autograph, Desmos): Dynamic scatter diagrams
- **Graphing calculators**: Required for A-level; students must be proficient in statistical functions
- **GeoGebra**: Free software with excellent statistics tools

The National Centre for Excellence in the Teaching of Mathematics (NCETM) provides guidance on integrating technology whilst maintaining conceptual understanding.

### Developing Statistical Literacy

Malcolm Swan's research emphasises that statistics education should develop critical consumers of data. Teaching should include:

- Evaluating statistical claims in media and advertising
- Discussing how statistics can be misleading (e.g., inappropriate averages, suppressed axes, cherry-picked correlations)
- Understanding sampling and whether data is representative
- Questioning data sources and collection methods

Anne Watson's work on reasoning in mathematics highlights the importance of "what if?" questioning: What if we removed this outlier? What if the sample size were larger? What happens to the mean if we add this value?

### Common Teaching Pitfalls to Avoid

1. **Over-reliance on algorithms**: Teaching procedures without conceptual foundation
2. **Neglecting context**: Calculating statistics without interpreting meaning
3. **Treating correlation mechanistically**: Not discussing causation or lurking variables
4. **Ignoring data quality**: Assuming all data is accurate and representative
5. **Limited data sets**: Using only clean, small datasets rather than messy, real-world data

## Cross-Curricular Connections

Statistical measures have natural connections to:

- **Science**: Experimental data analysis, presenting findings
- **Geography**: Demographic data, climate statistics, development indicators
- **Physical Education**: Performance statistics, health data
- **Economics/Business Studies**: Financial data, market research
- **Psychology/Social Sciences**: Survey data, behavioural studies

David Spiegelhalter's advocacy for statistical literacy emphasises that these measures are tools for understanding the world, not isolated mathematical exercises.

## Differentiation and Progression

### Supporting Struggling Students

- Begin with small, discrete datasets before introducing frequency tables
- Use physical representations (e.g., stacking cubes to find median)
- Provide structured templates for calculations
- Focus on conceptual understanding (what does this mean?) before procedures
- Use technology to handle calculations, allowing focus on interpretation

### Stretching High Attainers

- Investigate properties mathematically (e.g., prove the mean is affected by outliers more than median)
- Explore weighted averages and harmonic means
- Consider non-parametric alternatives to PMCC
- Analyse complex, multivariable datasets
- Critique statistical claims in academic papers or policy documents
- Bridge to inferential statistics (confidence intervals, significance testing)

## Research Evidence and Future Directions

Research by Watson and Moritz (2000) on statistical literacy demonstrates that understanding develops through levels: idiosyncratic (personal interpretation), transitional (incomplete formal understanding), and quantitative (complete formal understanding with critical analysis). Teachers should recognise students' current level and provide appropriate scaffolding.

Recent curriculum reviews in England have emphasised the importance of statistics as a distinct discipline, not merely a branch of mathematics. The Royal Statistical Society's advisory work with the Department for Education has advocated for more sophisticated treatment of uncertainty, data quality, and critical interpretation—themes that permeate David Spiegelhalter's public work.

The COVID-19 pandemic dramatically illustrated the importance of statistical literacy in public discourse. Education researchers, including those at the Cambridge Mathematics framework, are developing materials that connect classroom statistics to real-world decision-making under uncertainty.

## Conclusion

Statistical measures of averages, spread, and correlation provide students with essential tools for understanding quantitative information in academic, professional, and civic contexts. Effective teaching moves beyond procedural calculation to develop conceptual understanding, critical evaluation, and the ability to communicate statistical findings. By following the progressive curriculum structure from Key Stage 2 through A-level, and incorporating insights from Watson, Swan, Sherratt, and Spiegelhalter, teachers can develop statistically literate students capable of engaging meaningfully with data-driven arguments and claims.