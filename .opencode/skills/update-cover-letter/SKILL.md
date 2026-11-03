---
name: Update Cover Letter
description: Tailor latex/coverletter.tex to match any job description by dynamically extracting skills from the CV and following AGENTS.md.
---

# Update Cover Letter Skill

Use this skill to tailor `latex/coverletter.tex` for a target job posting by dynamically pulling technical background from the CV and adhering to the directives in `AGENTS.md`.

## 1. Input Sources

1. **Target Job Description**:
   - Provided either in the conversation prompt or located in `app/data/JOB_DESCRIPTION.md`.
   - Identify: Company name, role title, technical requirements, domain focus, and key responsibilities.
2. **Resume Files (Source of Truth for Background & Skills)**:
   - Read the CV files in `latex/cv/*.tex` (e.g., `1-summary.tex`, `2-work.tex`, `4-technologies.tex`, `6-projects.tex`) and `latex/header.tex` to discover relevant experience, tools, roles, and accomplishments.
   - **Do not invent** technologies, experiences, or claims not present in the CV files.
3. **Target File**:
   - Read `latex/coverletter.tex` to preserve document structure, styling, and commands.
4. **Directives & Constraints**:
   - Refer to `AGENTS.md` for career philosophy, communication boundaries, tone directives, and specific exclusions.

---

## 2. Style & Tone Guidelines (per `AGENTS.md`)

- **Tone**: Modest, concise, factual, and authentic.
- **Language**: Keep wordings technical and concrete. Use direct, active verbs describing systems, implementations, and tools. Avoid vague, qualitative, or fancy descriptors (e.g., do not use words like *"solid"*, *"deep"*, *"strong"*, *"exceptional"*).
- **No Fluff or Corporate Buzzwords**: Avoid empty corporate buzzwords and superlative hype (e.g., avoid *"driving"*, *"leveraging"*, *"seamless"*, *"best"*, *"cutting-edge"*, *"incredibly"*, *"unbelievable"*).
- **Vocabulary Level & Phrasing**:
  - Keep the exact same difficulty and wording style already established in `latex/coverletter.tex`.
  - As a non-native English speaker, use plain, straightforward, and technical phrasing rather than complex or elevated idioms (e.g., use *"interested in"* instead of *"drawn to"*).
  - Preserve the existing sentence patterns and phrasing rather than unnecessarily rephrasing into overly sophisticated English.
- **Scope & Exclusions**: Follow all profile guardrails and exclusions detailed in `AGENTS.md` (e.g., regarding specific past publications or overstating daily scope).
- **No Laundry-Listing (Do Not Copy-Paste the Resume)**:
  - Do NOT list experiences, past companies, or technologies one after another in a row (e.g., avoid listing "At ABB I did X, at FBK I did Y, and I also have experience with Z and W").
  - A cover letter is not a chronological recap or a duplicate of the CV. Focus selectively on the **single most important and relevant experience or project** that directly addresses the target role's primary challenge.

---

## 3. Section Customization Guidelines

Modify the body sections inside `\begin{cvletter} ... \end{cvletter}` in `latex/coverletter.tex`:

### `\lettersection{Summary}`
- State the candidate's name (from `latex/header.tex`), the role being applied for, and the company name.
- Provide a brief statement of current technical profile and core strengths directly matching the role.
- Do not rattle off past employers or consecutive job titles here.

### `\lettersection{Why <Company Name>?}`
- Replace any placeholders in the section title and body with the target company's name.
- **Human & Specific Motivation**:
  - Never write generic buzzword recaps of the company's marketing copy (e.g., avoid *"I am drawn to [Company] because of your focus on building production AI applications, agentic workflows, and enterprise automation"*).
  - Instead, identify **1 or 2 very specific, concrete technical aspects, problems, or product mechanisms** from the job description that connect directly to your own hands-on experience and genuine curiosity (e.g., how the company handles a specific data reliability challenge, scales an internal tool, or structures model deployments).
  - Use simple, human phrasing like *"I am interested in [Company] because..."* or *"I am curious about how [Company]..."* (never *"I am drawn to"*).
  - Maintain the authentic transition motivation: moving from larger corporations to a smaller, more focused team where adoption of new technologies is faster and cycles from development to production are shorter.

### `\lettersection{Why Me?}`
- Focus on depth over breadth: identify the single most critical challenge or requirement from the job description.
- Highlight only the most relevant project or hands-on capability from `latex/cv/*.tex` that proves you can solve that core problem.
- Explain concrete, practical details of that specific work rather than stringing together multiple past companies or tools.
- Keep the narrative authentic and focused on how your hands-on background bridges technical needs.

---

## 4. Execution Rules

- Use the `edit` tool to update `latex/coverletter.tex`.
- Keep changes clean, concise, and syntactically valid LaTeX.
- **Do not execute any git commands** (e.g., `git diff`, `git status`, `git commit`, `git reset`, `git checkout`).
- **Do not run ad-hoc verification scripts or compile LaTeX** after modifying files unless explicitly requested by the user.
