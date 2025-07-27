import concurrent.futures
import os
import time
from contextlib import redirect_stdout
from time import sleep

import streamlit as st
from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model

from utils.utils import RESUME_FILES, files_exist

INSTRUCTIONS = r"""
Intrustions:
- For every change you do the tone must remain modest, factual, and free from buzzwords and corporate jargon. Never use adjectives or superlative words like: 'best', 'complex', 'strong', 'leveraging', 'seamless' etc.
- JOB_DESCRIPTION.md highlights the skills in ***bold italic***. Reflect only these skills, or those already mentioned in the resume. If a skill in the JOB_DESCRIPTION.md is not in ***bold italic*** do NOT mention it.
- Do not ask me to run any command, such as 'Run shell command?', or 'Add file to the chat?'.
"""

PROMPT_RESUME_SUMMARY = rf"""
{INSTRUCTIONS}
(Prompt Resume 1 - v9)

In section 'Summary':
- Update summary mentioning my skill and my work experience relevant for this job.
- Do not mention specific technologies like Docker, Python, etc.
- Do not mention the paper publication.
- Write max 100 words.
"""

PROMPT_RESUME_WORK = rf"""
{INSTRUCTIONS}
(Prompt Resume 2 - v9)

In section 'Work Experience':
- Rank the bullet points by relevance for this job posting.
"""

PROMPT_RESUME_TECH = rf"""
{INSTRUCTIONS}
(Prompt Resume 3 - v9)

In section 'Relevant Technologies', for each section:
- Write the technologies specified in 'Always show', plus add the relevant technologies in 'Optional', plus the relevant technologies in ***bold italic*** in the JOB_DESCRIPTION.md. From the JOB_DESCRIPTION.md do NOT add technologies if they are not underlined in ***bold italic***.
- Rank them by relevance for this job posting, starting with the most important.
"""


PROMPT_RESUME_KEYWORDS = rf"""
{INSTRUCTIONS}
(Prompt Resume 5 - v9)

In section 'Keywords':
- Gather all the keywords missing from the resume files, but present in JOB_DESCRIPTION.md, that would improve the resume score of an ATS keyword scanner.
- Include 10 to 20 of them.
"""

PROMPT_RESUME_PROJ = rf"""
{INSTRUCTIONS}
(Prompt Resume 4 - v9)

In section 'Extra Projects':
- Keep 4 to 6 projects removing the ones which are irrelevant.
- Rank them by relevance for this job posting, starting with the most important.
- Do not change name or description.
"""

PROMPT_LETTER = rf"""
{INSTRUCTIONS}
(Prompt Cover Letter - v9)

Update the cover letter (in coverletter.tex) to match the requirements of a new job description (in JOB_DESCRIPTION.md) for the job posting new company, considering the resume.
In each of the 3 sections pick up muliple points brought up from the job description and resume.

Instructions:
- Do not mention anywhere the Nature publication.
- Do not change the word choice and tone.

Specific to 'Why Company' section:
- Keep the reason that I want to change from a large corporation to a smaller company.
- Replace 'COMPANY-NAME' with the company name from the job description.
"""

PROMPT_EMAIL = rf"""
{INSTRUCTIONS}
(Prompt Email Draft - v9)

Rewrite the EMAIL_DRAFT.md to fit the JOB_DESCRIPTION.md. Rewrite the 2 questions to fit the job description.
- Keep them without corporate jargon and keep the tone very technical.
- Do not write my experience, only make the questions.
"""


def _get_coder(fnames: list) -> Coder:
    """Create Aider Coder with specified files.

    Args:
        fnames (list): Files the Coder can view and interact with
    """
    model = Model("gemini-2.5-pro")
    # model = Model("gemini-2.5-flash-lite")
    coder = Coder.create(main_model=model, auto_commits=False)

    # Check for file existance
    files_exist(fnames)
    for fname in fnames:
        coder.add_rel_fname(fname)
    return coder


def _prompt(prompt, prompt_name, files):
    """Run Aider command and return the result and status."""
    coder = _get_coder(files)
    start = time.time()

    aider_output = coder.run(prompt)
    code = f"{prompt}\n\n---\n\n{aider_output}"
    exec_time = time.time() - start
    cost = coder.total_cost
    return prompt_name, code, exec_time, cost


def update_resume():
    """
    Update resume files with Aider to match the job description.
    """
    files = ["JOB_DESCRIPTION.md", *RESUME_FILES]
    prompts = [
        (PROMPT_RESUME_SUMMARY, "Summary", files),
        (PROMPT_RESUME_WORK, "Work", files),
        (PROMPT_RESUME_TECH, "Technologies", files),
        (PROMPT_RESUME_KEYWORDS, "Keywords", files),
        (PROMPT_RESUME_PROJ, "Projects", files),
    ]

    placeholders = {}
    for _, prompt_name, _ in prompts:
        placeholder = st.empty()
        expander = placeholder.expander(f"▷ {prompt_name}: Running...")
        expander.code("Processing...")
        placeholders[prompt_name] = placeholder

    # Discard output from coder.run(prompt)
    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull):
            # Parallel execution
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(_prompt, *p) for p in prompts]
                for future in concurrent.futures.as_completed(futures):
                    prompt_name, code_output, exec_time, cost = future.result()
                    status = f"✅ {prompt_name}: Done in {exec_time:.0f}s (${cost:.2f})"

                    placeholder = placeholders[prompt_name]
                    placeholder.empty()
                    with placeholder.expander(status):
                        st.code(code_output)


def update_cover_letter():
    """
    Update cover letter with Aider to match the job description.
    """
    files = ["JOB_DESCRIPTION.md", *RESUME_FILES, "coverletter.tex"]
    _prompt(PROMPT_LETTER, "Cover Letter", files)


def update_email():
    files = ["JOB_DESCRIPTION.md", *RESUME_FILES, "EMAIL_DRAFT.md"]
    _prompt(PROMPT_EMAIL, "Email", files)
