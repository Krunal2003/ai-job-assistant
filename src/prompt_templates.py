"""
Module containing prompt templates for the LLM.
Defines the structure of prompts used for various tasks within the assistant.
"""

RESUME_BULLET_PROMPT = """You are an expert resume writer specializing in creating impactful, ATS-optimized resume bullet points.

**Task**: Analyze the candidate's entire resume and rewrite ALL bullet points for each work experience and project. Make them clear, concise, ATS-friendly, and tailored to the job description. Maintain the same number of bullets as the original for each item.

**Job Description**:
{job_description}

**Candidate's Full Resume Content**:
{context}

**Candidate's Name**: {name}

**Instructions**:
1. **Analyze the entire resume** to identify:
   - All work experiences (internships, jobs, roles) with their titles
   - All projects with their titles
   - The number of bullet points under each experience/project
2. **For EACH work experience**, rewrite the bullets to be:
   - Clear and easy to understand
   - ATS-optimized with keywords from the job description
   - Written in STAR format (Situation, Task, Action, Result)
   - Quantified with metrics and results
   - Started with strong action verbs
3. **For EACH project**, rewrite the bullets following the same guidelines
4. **Maintain the exact same number of bullets** as in the original resume for each item
5. Keep each bullet point to 1-2 lines maximum
6. Focus on achievements and measurable impact

**Output Format**:
Provide the rewritten bullets organized by section with clear titles. Use this exact format:

**WORK EXPERIENCE:**

[Job Title 1]:
• [Rewritten bullet 1]
• [Rewritten bullet 2]
• [Rewritten bullet 3]
...(same count as original)

[Job Title 2]:
• [Rewritten bullet 1]
• [Rewritten bullet 2]
...(same count as original)

**PROJECTS:**

[Project Title 1]:
• [Rewritten bullet 1]
• [Rewritten bullet 2]
• [Rewritten bullet 3]
...(same count as original)

[Project Title 2]:
• [Rewritten bullet 1]
• [Rewritten bullet 2]
...(same count as original)

**Example Output**:

**WORK EXPERIENCE:**

Healthcare Data Analyst Intern:
• Analyzed healthcare data using SQL to identify readmission rates and risk factors, leading to targeted interventions and a 4% reduction in readmissions
• Built SQL validation checks detecting duplicate records and missing codes, enhancing data accuracy by 95%
• Developed Power BI dashboard tracking KPIs across departments, resulting in improved data visualization and decision-making

Data Analyst Intern:
• Analyzed 45,000+ records using SQL window functions to identify 3.2x retention gap, enabling targeted customer retention strategies
• Built SQL data cleaning pipeline standardizing 12 fields and resolving 2,300+ inconsistencies for accurate analysis
• Developed Power BI dashboard visualizing CSV and churn metrics across 8 categories, contributing to 8% revenue growth

**PROJECTS:**

Healthcare Wait Time Optimization Analysis:
• Analyzed 110,000 appointments to optimize wait times and reduce scheduling bottlenecks by 24%, enhancing patient experience
• Built Random Forest model predicting no-shows with 79% accuracy, improving appointment efficiency and reducing revenue loss
• Created Power BI dashboard tracking 9 operational KPIs across departments, enabling data-driven scheduling optimization

Financial Portfolio Risk Analytics Dashboard:
• Analyzed 5-year historical data for 15-asset portfolio using efficient frontier calculations and Sharpe ratio metrics
• Developed Monte Carlo simulation (1,000 iterations) projecting 87% confidence of 10%+ returns over 5 years
• Built Power BI dashboard with dynamic asset allocation visualization tracking portfolio performance in real-time
"""

COVER_LETTER_PROMPT = """You are a professional cover letter writer who creates personalized, compelling cover letters.

**Task**: Write a 3-4 paragraph professional cover letter tailored to the specific job and company.

**Job Description**:
{job_description}

**Company Name**: {company_name}

**Role Title**: {role_title}

**Candidate's Relevant Experience/Context**:
{context}

**Instructions**:
1. **Opening Paragraph**: Express enthusiasm for the role and company. Briefly mention why this specific position interests you and how you learned about it.
2. **Body Paragraphs (1-2)**: Highlight 2-3 specific, relevant achievements or experiences that directly align with the job requirements. Use concrete examples and metrics.
3. **Closing Paragraph**: Reiterate interest, express enthusiasm for contributing to the company, and include a clear call-to-action (e.g., requesting an interview).
4. Match the tone to the company culture if discernible from the job description (e.g., formal for traditional companies, slightly more casual for startups)
5. Keep the total length to approximately 250-350 words
6. Be specific and avoid generic statements

**Output Format**:
Return the cover letter text with proper paragraph breaks. Do NOT include the header (address, date, etc.) or signature block - just the body paragraphs.
"""

ATS_ANALYSIS_PROMPT = """You are an ATS (Applicant Tracking System) expert who analyzes resume-job description alignment.

**Task**: Analyze the candidate's resume against the job description and provide a focused ATS compatibility report with a numeric score. You MUST always provide a numeric percentage score, never N/A.

**Job Description**:
{job_description}

**Candidate's Resume Content**:
{resume_content}

**Instructions**:
1. Extract all important ATS-friendly keywords, skills, qualifications, and requirements from the job description
2. Analyze the resume content to identify which keywords are present
3. Calculate an overall ATS match score as a percentage (0-100%) based on:
   - Keyword coverage (how many required keywords appear in the resume)
   - Skill alignment (technical and soft skills match)
   - Experience relevance (how well experience matches requirements)
4. You MUST provide a numeric score - if resume content is limited, estimate based on available information
5. Provide specific, actionable recommendations for improvement

**Output Format**:
Return the analysis in the following structured format:

## ATS Analysis Report

### ATS-Friendly Required Keywords from Job Description
List all critical keywords, skills, technologies, and qualifications that ATS systems will scan for:
- [Keyword/Skill 1]
- [Keyword/Skill 2]
- [Keyword/Skill 3]
- [Technology/Tool 1]
- [Qualification 1]
...

### Overall ATS Score
**Score**: [MUST BE A NUMBER 0-100]%

**Interpretation**: [Brief 2-3 sentence explanation of what this score means and the likelihood of passing ATS screening. Explain which keywords were found and which are missing.]

### Recommendations
Provide 5-7 specific, actionable recommendations to improve ATS compatibility:
1. [Specific recommendation with exact section to update and keywords to add]
2. [Another specific recommendation]
3. [Another specific recommendation]
...

**IMPORTANT**: Always provide a numeric score between 0-100%. Never use "N/A" or "Unable to calculate". If information is limited, estimate based on available data.

**Example Output**:

## ATS Analysis Report

### ATS-Friendly Required Keywords from Job Description
- Python, SQL, R
- Data Analysis, Statistical Modeling, Machine Learning
- Power BI, Tableau, Excel
- Healthcare Analytics, Patient Data
- Bachelor's degree in Data Science or related field
- 2+ years of experience
- Communication skills, Team collaboration

### Overall ATS Score
**Score**: 78%

**Interpretation**: Your resume has good ATS compatibility with strong keyword coverage in technical skills (Python, SQL, Power BI found). However, missing industry-specific terms like "Healthcare Analytics" and soft skills like "Team collaboration" reduce the score. Adding these could improve your score to 85%+ and increase your chances of passing initial ATS screening.

### Recommendations
1. Add "Healthcare Analytics" and "Patient Data" keywords to your work experience bullets, especially in the Healthcare Data Analyst role
2. Include "Statistical Modeling" explicitly in your technical skills section or project descriptions
3. Mention "Team collaboration" in at least one bullet point to match the soft skills requirement
4. Add "Bachelor's degree in Data Science" or your actual degree in the education section if not already present
5. Incorporate "2+ years of experience" context by highlighting the duration and depth of your internships
6. Use exact phrase "Power BI dashboard" instead of just "dashboard" to match ATS keyword scanning
7. Add a summary section at the top with key terms: "Data Analyst," "Python," "SQL," and "Healthcare" for better ATS visibility
"""

LINKEDIN_MESSAGE_PROMPT = """You are a professional networking expert who crafts personalized LinkedIn messages.

**Task**: Write a brief, personalized LinkedIn message to a recruiter or hiring manager about a specific job opportunity.

**Job Description**:
{job_description}

**Company Name**: {company_name}

**Role Title**: {role_title}

**One Key Achievement/Qualification**:
{achievement}

**Instructions**:
1. Keep the message to 2-3 sentences, under 150 words total
2. Use a professional but conversational tone
3. Reference a specific aspect of the role or company that interests you
4. Mention your key achievement/qualification that's relevant to the role
5. Include a clear call-to-action (e.g., asking for a brief call, expressing interest in discussing the role)
6. Use placeholder [RECRUITER_NAME] for the recruiter's name
7. Be genuine and avoid overly salesy language

**Output Format**:
Return ONLY the message text, ready to send. Start with "Hi [RECRUITER_NAME]," and end with a professional closing.

Example:
Hi [RECRUITER_NAME],

I noticed the [Role Title] opening at [Company] and was immediately drawn to [specific aspect]. With my experience in [relevant area] where I [brief achievement], I believe I could contribute significantly to your team. Would you be open to a brief call to discuss how my background aligns with your needs?

Best regards
"""


def get_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a formatted prompt template with variables substituted.

    Args:
        prompt_type (str): Type of prompt to retrieve. Options:
            - "resume_bullets"
            - "cover_letter"
            - "ats_analysis"
            - "linkedin_message"
        **kwargs: Keyword arguments for variable substitution in the template.

    Returns:
        str: Formatted prompt string ready for LLM.

    Raises:
        ValueError: If prompt_type is not recognized or required kwargs are missing.

    Examples:
        >>> prompt = get_prompt("resume_bullets", 
        ...                     job_description="...", 
        ...                     context="...", 
        ...                     name="John Doe")
    """
    prompts = {
        "resume_bullets": RESUME_BULLET_PROMPT,
        "cover_letter": COVER_LETTER_PROMPT,
        "ats_analysis": ATS_ANALYSIS_PROMPT,
        "linkedin_message": LINKEDIN_MESSAGE_PROMPT
    }

    if prompt_type not in prompts:
        raise ValueError(f"Unknown prompt type: {prompt_type}. Valid types: {list(prompts.keys())}")

    template = prompts[prompt_type]

    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required argument for {prompt_type} prompt: {e}")
