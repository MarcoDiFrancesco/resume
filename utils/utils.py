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


def browser_open_silent(link):
    """Open link in browser without printing debug output."""
    with open(os.devnull, "w") as devnull:
        subprocess.Popen(["open", link], stdout=devnull, stderr=devnull)


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
        "Aarhus": "Fiskergade 10, 8000 Aarhus Centrum, Denmark",
        "Copenhagen": "Kastruplundgade 58, 2770 Kastrup, Copenhagen, Denmark",
        # Switzerland
        "Basel": "Dornacherstrasse 192, 4053 Basel, Switzerland",
        "Bern": "Rathausgasse 75, 3011 Bern, Switzerland",
        "Geneva": "Rue Rothschild 28, 1202 Genève, Switzerland",
        "Lausanne": "Rue Marterey 15, 1005 Lausanne, Switzerland",
        "Lucerne": "Zürichstrasse 33, 6004 Luzern, Switzerland",
        "Lugano": "Via Silvio Calloni 2, 6900 Lugano, Switzerland",
        "St Gallen": "Zürcherstrasse 28, 9000 St. Gallen, Switzerland",
        "Zurich": "Maneggstrasse 41, 8041 Zürich, Switzerland",
        # Germany
        "Berlin": "Weinbergsweg 1a, 10119 Berlin, Germany",
        "Cologne": "Mauritiuswall 64-66, 50676 Köln, Germany",
        "Frankfurt": "Moselstraße 40, 60329 Frankfurt, Germany",
        "Munich": "Senefelderstraße 1, 80336 München, Germany",
        "Hamburg": "Steintorpl. 3, 20099 Hamburg, Germany",
        "Stuttgart": "Alexanderstraße 30, 70184 Stuttgart, Germany",
        # Luxembourg
        "Luxembourg": "2 Rue du Fort Olisy, 2261 Pafendall, Luxembourg",
        # Norway
        "Oslo": "Bunks at Rode, Københavngata 10, 0566 Oslo, Norway",
        # Austria
        "Salzburg": "Fürbergstraße 18-20, 5020 Salzburg, Austria",
        "Vienna": "Rechte Wienzeile 35, 1040 Wien, Austria",
    }
    assert city in addresses, f"City '{city}' not found in addresses."
    return addresses[city]


def print_page_location_info(notion_page):
    city = notion_page["properties"]["City"]["select"]["name"]
    my_address = get_my_address(notion_page)
    st.code(
        f"""
        ┌────────────────────────────────────────────────────────────────────────────
        │ Location
        ├────────────┬───────────────────────────────────────────────────────────────
        │ City       │ {city}
        │ My Address │ {my_address}
        │ My Phone   │ +45 91839615
        └────────────┴───────────────────────────────────────────────────────────────
        """
    )
