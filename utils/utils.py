from pathlib import Path
from git import Repo

def get_links_from_file(fname: str) -> list:
    with open(fname, "r") as file:
        links = file.readlines()
    # Remove trailing /n
    links = [link.strip() for link in links]
    return links

def check_files_existance(fnames):
    """Check if all input files are present."""
    for f in fnames:
        if not Path(f).exists():
            raise FileNotFoundError(f"File not found '{f}'")


def check_git_changes(fname):
    """Check resume.tex is the template, not adjusted for another job."""
    repo = Repo(".")
    # Check if repo is in a detached HEAD state
    assert not repo.head.is_detached, "Go to HEAD state: 'git switch master'"

    changed_files = [item.a_path for item in repo.index.diff(None)]
    assert (
        fname not in changed_files
    ), f"{fname} has been modified. Reset it to the original template."


def has_job_description():
    """Check if JOB_DESCRIPTION.md is not empty."""
    with open("JOB_DESCRIPTION.md") as f:
        assert f.read().strip(), "JOB_DESCRIPTION.md is empty."
