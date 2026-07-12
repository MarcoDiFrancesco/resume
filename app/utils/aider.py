import concurrent.futures
import subprocess
import time
from pathlib import Path

import streamlit as st

from app.config import (
    AIDER_MODEL,
    AIDER_SCRIPT_PATH,
    COVER_LETTER_FILE,
    JOB_DESCRIPTION_FILE,
    PROMPT_HEADER,
    PROMPT_KEYWORDS,
    PROMPT_LETTER,
    PROMPT_SUMMARY,
    PROMPT_TECHNOLOGIES,
    RESUME_FILES,
)


def _prompt(prompt_file, prompt_name, input_files):
    """Run Aider command and return the result and status."""
    start = time.time()
    missing = [f for f in [prompt_file, *input_files] if not Path(f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing files for prompt {prompt_name}: {missing}")
    command = [
        AIDER_SCRIPT_PATH,
        *input_files,
        "--model",
        AIDER_MODEL,
        "--message-file",
        prompt_file,
        # Give Aider a large token limit for the repository map to ensure full context
        "--map-tokens",
        "256000",
        "--no-show-model-warnings",
        # "--yes", # Can be used if it's prompting for questions
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    aider_output = result.stdout if result.returncode == 0 else result.stderr
    code = f"Prompt from {prompt_file}\n\n---\n\n{aider_output}"
    exec_time = time.time() - start
    return prompt_name, code, exec_time


def update_resume():
    """Update resume files with Aider to match the job description."""
    input_files = [JOB_DESCRIPTION_FILE, *RESUME_FILES]
    prompts = [
        (PROMPT_SUMMARY, "Summary"),
        (PROMPT_TECHNOLOGIES, "Technologies"),
        (PROMPT_KEYWORDS, "Keywords"),
        (PROMPT_HEADER, "Header"),
    ]
    placeholders = {}
    for _, prompt_name in prompts:
        placeholder = st.empty()
        expander = placeholder.expander(f"▷ {prompt_name}: Running...")
        expander.code("Processing...")
        placeholders[prompt_name] = placeholder

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
    files = [JOB_DESCRIPTION_FILE, *RESUME_FILES, COVER_LETTER_FILE]
    _, code_output, exec_time = _prompt(PROMPT_LETTER, "Cover Letter", files)
    st.code(code_output)
