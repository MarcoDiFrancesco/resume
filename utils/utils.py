from pathlib import Path
import dateutil.parser
from git import Repo
import sys
import os
import webbrowser
import subprocess
import datetime
import dateutil

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
            raise FileNotFoundError(
                f"[📂] File not found '{f}'. Is it the right directory?"
            )


def check_page_content(page_content: str) -> str:
    """Check if page content has italic-bold markdown text."""
    if "***" in page_content:
        return True
    return False


def copy_text_to_file(text: str, fname: str):
    """Copy text to file."""
    with open(fname, "w") as file:
        file.write(text)

    print("[📂] Notion page content copied to JOB_DESCRIPTION.md")


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
        print(f"[📌] Git changes in '{fname}' were reset.")


def browser_open_silent(link):
    """Open link in browser without printing debug output."""
    with open(os.devnull, "w") as devnull:
        subprocess.Popen(["open", link], stdout=devnull, stderr=devnull)
    print(f"[🌐] Opened in browser: {link}")


def get_my_address(notion_page) -> str:
    """
    Get address from city. Addresses are hard-coded.

    Example:
    >>> _get_address(notion_page)
    'Maneggstrasse 41, 8041 Zürich, Switzerland'
    """
    city = notion_page["properties"]["City"]["select"]["name"]
    addresses = {
        # Main cities
        "Copenhagen": "Kastruplundgade 58, 2770 Kastrup, Copenhagen, Denmark",
        "Zurich": "Maneggstrasse 41, 8041 Zürich, Switzerland",
        # Switzerland
        "Basel": "Dornacherstrasse 192, 4053 Basel, Switzerland",
        "Bern": "Rathausgasse 75, 3011 Bern, Switzerland",
        "Geneva": "Rue Rothschild 28, 1202 Genève, Switzerland",
        "Lausanne": "Rue Marterey 15, 1005 Lausanne, Switzerland",
        "Lucerne": "Zürichstrasse 33, 6004 Luzern, Switzerland",
        "Lugano": "Via Silvio Calloni 2, 6900 Lugano, Switzerland",
        "St Gallen": "Zürcherstrasse 28, 9000 St. Gallen, Switzerland",
        # Germany
        "Munich": "Senefelderstraße 1, 80336 München, Germany",
        "Hamburg": "Steintorpl. 3, 20099 Hamburg, Germany",
        # Norway
        "Oslo": "Bunks at Rode, Københavngata 10, 0566 Oslo, Norway",
        # Austria
        "Vienna": "Rechte Wienzeile 35, 1040 Wien, Austria",
        
    }
    assert city in addresses, f"City '{city}' not found in addresses."
    return addresses[city]


def print_page_summary(notion_page):
    title = "".join(notion_page["properties"]["Position"]["title"][0]["plain_text"])
    city = notion_page["properties"]["City"]["select"]["name"]
    my_address = get_my_address(notion_page)
    time_delta = datetime.datetime.now() - dateutil.parser.parse(
        notion_page["created_time"], ignoretz=True
    )
    if time_delta.days >= 2:
        time_delta_str = f"{time_delta.days} days ago"
    if time_delta.days >= 1:
        time_delta_str = f"{time_delta.days} day ago"
    elif time_delta.seconds > 60 * 60:
        time_delta_str = f"{time_delta.seconds // (60*60)} hours ago"
    else:
        time_delta_str = f"{time_delta.seconds // 60} minutes ago"

    print(
        f"""
=== Job posting details ===
    Title: {title}
    Page created: {time_delta_str}
    City: {city}
    My Address: {my_address}
    Phone Number: +45 91839615
"""
    )


def print_page_requirements(requirements):
    print(
        f"""
=== Posting requirements ===
    {requirements['req_lang']}
    {requirements['req_stud']}
    {requirements['req_phd']}
"""
    )
