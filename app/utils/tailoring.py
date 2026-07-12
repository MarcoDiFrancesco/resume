import streamlit as st

from app.config import (
    COVER_LETTER_FILE,
    EMAIL_DRAFT_FILE,
    JOB_DESCRIPTION_FILE,
    RESUME_FILES,
    RESUME_MAIN_FILE,
)
from app.utils import aider
from app.utils.helpers import (
    compile_latex,
    copy_text_to_file,
    reset_git_changes,
)
from app.utils.notion import Notion


def tailoring_links(notion: Notion):
    """Display buttons to open the current posting in Notion and LinkedIn."""
    notion_url = notion.page_data["url"]
    linkedin_url = notion.page_data["properties"]["URL"]["url"]

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("💼 Notion", notion_url, use_container_width=True)
    with col2:
        st.link_button("🟦 LinkedIn", linkedin_url, use_container_width=True)


def tailoring_update(notion: Notion):
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
        compile_latex(RESUME_MAIN_FILE)

    if st.button("2️⃣ Update Cover letter", **button_config):
        with st.status("Cover letter", expanded=True):
            reset_git_changes([COVER_LETTER_FILE])
            aider.update_cover_letter()
            compile_latex(COVER_LETTER_FILE)

    if st.button("3️⃣ Update Email", **button_config):
        with st.status("Email", expanded=True):
            reset_git_changes([EMAIL_DRAFT_FILE])
            aider.update_email()
