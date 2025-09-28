import os

import streamlit as st

from utils import aider, posting
from utils.notion import Notion
from utils.utils import (
    RESUME_FILES,
    copy_text_to_file,
    reset_git_changes,
)


def db_buttons():
    col1, col2, col3 = st.columns(3)
    with col1:
        # Button to open Notion database
        st.link_button(
            "📂 Notion DB",
            f"https://notion.so/{os.environ['NOTION_DB_ID']}",
            type="primary",
            use_container_width=True,
        )
    with col2:
        if st.button(
            "🔄 New posting",
            use_container_width=True,
        ):
            posting.fetch_posting.clear()
    with col3:
        if st.button(
            "🪥 Clean Markdown pages",
            use_container_width=True,
        ):
            posting.clean_all_pages_md()


def browser_buttons(notion):
    notion_url = notion.page["url"]
    linkedin_url = notion.page["properties"]["URL"]["url"]
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("💼 Notion", notion_url, use_container_width=True)
    with col2:
        st.link_button("🟦 LinkedIn", linkedin_url, use_container_width=True)


def update_buttons(notion: Notion):
    check_pass = notion.check_page_properties()

    st.subheader("Finetune")

    if check_pass:
        page_descr = notion.get_descr_with_props()
        copy_text_to_file(page_descr, "JOB_DESCRIPTION.md")

    button_kwargs = {
        "type": "primary",
        "disabled": not check_pass,
        "use_container_width": True,
    }
    if st.button("1️⃣ Update Resume", **button_kwargs):
        # Removed, since expanders can't be nested inside expanders
        # with st.status("Resume", expanded=True):
        reset_git_changes(RESUME_FILES)
        aider.update_resume()
        notion.set_applied_and_date()

    if st.button("2️⃣ Update Cover letter", **button_kwargs):
        with st.status("Cover letter", expanded=True):
            reset_git_changes(["coverletter.tex"])
            aider.update_cover_letter()

    if st.button("3️⃣ Update Email", **button_kwargs):
        with st.status("Email", expanded=True):
            reset_git_changes(["EMAIL_DRAFT.md"])
            aider.update_email()


def main():
    st.set_page_config(page_title="Resume Finetune", layout="wide")
    c1, c2 = st.columns([1, 1])
    # Left column for job posting info
    with c1:
        st.header("Posting")
        db_buttons()
        notion = posting.fetch_posting()
    # Right column for updating CV
    with c2:
        st.header("Update CV/Cover Letter")
        browser_buttons(notion)
        update_buttons(notion)
        st.warning("Check Miro for new project setup!")


if __name__ == "__main__":
    main()
