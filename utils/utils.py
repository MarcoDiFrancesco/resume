from pathlib import Path
from git import Repo

# def get_links_from_file(fname: str) -> list:
#     with open(fname, "r") as file:
#         links = file.readlines()
#     # Remove trailing /n
#     links = [link.strip() for link in links]
#     return links


def check_files_existance(fnames):
    """Check if all input files are present."""
    for f in fnames:
        if not Path(f).exists():
            raise FileNotFoundError(f"File not found '{f}'")


def has_git_changes(fname):
    """Check resume.tex is the template, not adjusted for another job."""
    repo = Repo(".")
    # Check if repo is in a detached HEAD state
    assert not repo.head.is_detached, "Go to HEAD state: 'git switch master'"

    changed_files = [item.a_path for item in repo.index.diff(None)]
    return fname in changed_files
