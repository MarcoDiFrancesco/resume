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


def reset_git_changes(fnames):
    """
    Check if file has git changes.
    For example if 'resume.tex' is not template, reset it to template.
    """

    repo = Repo(".")
    # Check if repo is in a detached HEAD state
    assert not repo.head.is_detached, "Go to HEAD state: 'git switch master'"

    changed_files = [item.a_path for item in repo.index.diff(None)]
    for fname in fnames:
        if fname in changed_files:
            # Reset git changes. Only unstaged changes are reset.
            repo.git.checkout("--", fname)
            st.text(f"[📌] Git changes in '{fname}' were reset.")


def compile_latex(file_path: str):
    """
    Compile a LaTeX file using lualatex.
    """
    path = Path(file_path)
    if not path.exists():
        st.error(f"LaTeX file not found: {file_path}")
        return

    work_dir = path.parent
    file_name = path.name
    build_dir = work_dir / "build"
    build_dir.mkdir(exist_ok=True)

    with st.spinner(f"Compiling {file_name}..."):
        try:
            result = subprocess.run(
                [
                    "lualatex",
                    "-output-directory=build",
                    "-interaction=nonstopmode",
                    file_name,
                ],
                cwd=work_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                st.success(f"Successfully compiled {file_name}")
            else:
                st.error(f"Failed to compile {file_name}")
                with st.expander("Compilation Logs"):
                    st.code(result.stdout)
                    if result.stderr:
                        st.code(result.stderr)
        except Exception as e:
            st.error(f"Error compiling LaTeX: {str(e)}")
