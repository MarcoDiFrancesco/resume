import datetime
import os
import subprocess
from pathlib import Path

import dateutil
import dateutil.parser
import streamlit as st
from git import Repo


def files_exist(fnames):
    """Check if all input files are present."""
    for f in fnames:
        if not Path(f).exists():
            raise FileNotFoundError(
                f"[📂] File not found '{f}'. Did you run the script in the 'resume' directory?"
            )


def page_is_underlined(page_content: str) -> bool:
    """Check if page content has italic-bold markdown text."""
    if "***" in page_content:
        return True
    return False


def copy_text_to_file(text: str, fname: str):
    """Copy text to file."""
    with open(fname, "w") as file:
        file.write(text)


def reset_git_changes(fname):
    """
    Check if file has git changes.
    For example if 'resume.tex' is not template, reset it to template.
    """

    repo = Repo(".")
    # Check if repo is in a detached HEAD state
    assert not repo.head.is_detached, "Go to HEAD state: 'git switch master'"

    changed_files = [item.a_path for item in repo.index.diff(None)]
    if fname in changed_files:
        # Reset git changes. Only unstaged changes are reset.
        repo.git.checkout("--", fname)
        st.text(f"[📌] Git changes in '{fname}' were reset.")
