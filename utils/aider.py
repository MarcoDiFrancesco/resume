import io
import os
import re
import sys
import time

import streamlit as st
from aider.coders import Coder
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
- Gather all the keywords missing from the resume.tex but present in JOB_DESCRIPTION.md, that would improve the resume score of an ATS keyword scanner.
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

Update the cover letter (in coverletter.tex) to match the requirements of a new job description (in JOB_DESCRIPTION.md) for the job posting new company, considering the resume (in resume.tex).
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


class Aider:
    def __init__(self):
        self.model = Model("gemini-2.5-pro")

    def _reset(self):
        """Reset Aider coder"""
        self.coder: Coder = Coder.create(main_model=self.model, auto_commits=False)

    def _add_files(self, fnames):
        files_exist(fnames)
        for fname in fnames:
            self.coder.add_rel_fname(fname)

    def _prompt(self, prompt, file, num, tot):
        """Run Aider command and show progress in the dashboard as a text box."""
        txt_box = st.text(f"[Aider] - {file} prompt {num}/{tot}. Running...")
        start = time.time()

        # Capture output from self.coder.run(prompt)
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.coder.run(prompt)
        sys.stdout = sys.__stdout__
        result = captured_output.getvalue()
        # Remove aider line coloring escape sequences
        result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        st.code(result)
        end = time.time()
        txt_box.text(
            f"[Aider] - {file} prompt {num}/{tot}. Done in {end-start:.0f} sec. Session cost: {self.coder.total_cost:.2f}$"
        )

    def update_resume(self):
        """
        Update resume.tex with Aider to match the job description.
        """
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", *RESUME_FILES])
        self._prompt(PROMPT_RESUME_SUMMARY, "Resume", 1, 5)
        self._prompt(PROMPT_RESUME_WORK, "Resume", 2, 5)
        self._prompt(PROMPT_RESUME_TECH, "Resume", 3, 5)
        self._prompt(PROMPT_RESUME_PROJ, "Resume", 4, 5)
        self._prompt(PROMPT_RESUME_KEYWORDS, "Resume", 5, 5)

    def update_cover_letter(self):
        """
        Update coverletter.tex with Aider.
        """
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", *RESUME_FILES, "coverletter.tex"])
        self._prompt(PROMPT_LETTER, "Cover Letter", 1, 1)

    def update_email(self):
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", *RESUME_FILES, "EMAIL_DRAFT.md"])
        self._prompt(PROMPT_EMAIL, "Email", 1, 1)
