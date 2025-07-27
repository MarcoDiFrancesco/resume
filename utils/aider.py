import concurrent.futures
import os
import subprocess
import time
from contextlib import redirect_stdout
from time import sleep

import streamlit as st
from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model

from utils.utils import RESUME_FILES, files_exist

PROMPT_LETTER = rf"""
ADD INSTRUCTIONS...

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
ADD INSTRUCTIONS...

(Prompt Email Draft - v9)

Rewrite the EMAIL_DRAFT.md to fit the JOB_DESCRIPTION.md. Rewrite the 2 questions to fit the job description.
- Keep them without corporate jargon and keep the tone very technical.
- Do not write my experience, only make the questions.
"""


def _prompt(prompt_file, prompt_name, input_files):
    """Run Aider command and return the result and status."""
    start = time.time()
    files_exist([prompt_file, *input_files])
    command = [
        "/home/marco/scripts/aider",
        *input_files,
        "--model",
        "gemini-2.5-pro",
        "--message-file",
        prompt_file,
        # "--yes", # Can be used if it's prompting for questions
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    aider_output = result.stdout if result.returncode == 0 else result.stderr
    code = f"Prompt from {prompt_file}\n\n---\n\n{aider_output}"
    exec_time = time.time() - start
    return prompt_name, code, exec_time


def update_resume():
    """Update resume files with Aider to match the job description."""
    input_files = ["JOB_DESCRIPTION.md", *RESUME_FILES]
    prompts = [
        ("prompts/1-summary.txt", "Summary"),
        ("prompts/2-work.txt", "Work"),
        ("prompts/4-technologies.txt", "Technologies"),
        ("prompts/5-keywords.txt", "Keywords"),
        ("prompts/6-projects.txt", "Projects"),
    ]
    placeholders = {}
    for _, prompt_name in prompts:
        placeholder = st.empty()
        expander = placeholder.expander(f"▷ {prompt_name}: Running...")
        expander.code("Processing...")
        placeholders[prompt_name] = placeholder

    # Parallel execution
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(_prompt, p[0], p[1], input_files) for p in prompts]
        for future in concurrent.futures.as_completed(futures):
            prompt_name, code_output, exec_time = future.result()
            status = f"✅ {prompt_name}: Done in {exec_time:.0f}s"

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
    raise NotImplementedError()


def update_email():
    files = ["JOB_DESCRIPTION.md", *RESUME_FILES, "EMAIL_DRAFT.md"]
    _prompt(PROMPT_EMAIL, "Email", files)
    raise NotImplementedError()
