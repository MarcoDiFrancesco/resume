import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import streamlit as st

from app.config import (
    COVER_LETTER_FILE,
    EMAIL_DRAFT_FILE,
    JOB_DESCRIPTION_FILE,
    NOTION_PURPOSE_PAGE_URL,
    RESUME_FILES,
)
from app.utils import aider, posting
from app.utils.notion import Notion
from app.utils.helpers import (
    copy_text_to_file,
    reset_git_changes,
)


def db_buttons():
    """Display buttons for database navigation and actions."""
    col1, col2 = st.columns(2)
    with col1:
        st.link_button(
            "🍃 Finding My Purpose",
            NOTION_PURPOSE_PAGE_URL,
            type="primary",
            use_container_width=True,
        )
    with col2:
        st.link_button(
            "📂 Notion DB",
            f"https://notion.so/{os.environ['NOTION_DB_ID']}",
            type="primary",
            use_container_width=True,
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New posting", use_container_width=True):
            # Clear the cached posting and fetch a new one
            posting.fetch_posting.clear()
    with col2:
        if st.button("🪥 Clean Markdown pages", use_container_width=True):
            posting.clean_all_pages_md()
    with col3:
        if st.button("⿻ Find Duplicates", use_container_width=True):
            posting.find_all_duplicates()


def browser_buttons(notion: Notion):
    """Display buttons to open the current posting in Notion and LinkedIn."""
    notion_url = notion.page["url"]
    linkedin_url = notion.page["properties"]["URL"]["url"]

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("💼 Notion", notion_url, use_container_width=True)
    with col2:
        st.link_button("🟦 LinkedIn", linkedin_url, use_container_width=True)


def update_buttons(notion: Notion):
    """Display buttons for updating resume, cover letter, and email."""
    is_valid = notion.check_page_properties()
    st.subheader("Finetune")

    if is_valid:
        page_descr = notion.get_descr_with_props()
        copy_text_to_file(page_descr, JOB_DESCRIPTION_FILE)

    button_config = {
        "type": "primary",
        "disabled": not is_valid,
        "use_container_width": True,
    }

    if st.button("1️⃣ Update Resume", **button_config):
        reset_git_changes(RESUME_FILES)
        aider.update_resume()
        notion.set_applied_and_date()

    if st.button("2️⃣ Update Cover letter", **button_config):
        with st.status("Cover letter", expanded=True):
            reset_git_changes([COVER_LETTER_FILE])
            aider.update_cover_letter()

    if st.button("3️⃣ Update Email", **button_config):
        with st.status("Email", expanded=True):
            reset_git_changes([EMAIL_DRAFT_FILE])
            aider.update_email()


def main():
    st.set_page_config(page_title="Resume Finetune", layout="wide")

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.header("Posting")
        db_buttons()
        notion = posting.fetch_posting()

    with right_col:
        st.header("Update CV/Cover Letter")
        browser_buttons(notion)
        update_buttons(notion)
        st.warning("Check Miro for new project setup!")


if __name__ == "__main__":
    main()
