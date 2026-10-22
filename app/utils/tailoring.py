from pathlib import Path

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from app.config import (
    COVER_LETTER_FILE,
    COVER_LETTER_PDF_FILE,
    JOB_DESCRIPTION_FILE,
    RESUME_FILES,
    RESUME_MAIN_FILE,
    RESUME_PDF_FILE,
)
from app.utils import aider
from app.utils.helpers import (
    compile_latex,
    copy_text_to_file,
    page_is_underlined,
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


def tailoring_check(notion: Notion) -> bool:
    """
    Check the following properties:
    - Underlining: if the page description contains bold-italic highlights
    """
    # Fetch the page again by URL to ensure we have the latest edits from Notion
    url = notion.page_data["properties"]["URL"]["url"]
    query = notion._query_db(
        filter={
            "property": "URL",
            "url": {"equals": url},
        }
    )
    if len(query["results"]) > 1:
        st.error("Duplicate posting with same URL.")
        return False
    if len(query["results"]) == 0:
        st.error("Posting not found in Notion.")
        return False
    notion.page = query["results"][0]

    err_message = st.empty()
    checks_ok = False

    if not page_is_underlined(notion.get_descr()):
        err_message.markdown(
            "❌ Highlighting of Notion page in ***bold-italic*** not found → Edit Notion page and rerun checks"
        )
    else:
        err_message.markdown(
            "✅ Highlighting of Notion page in ***bold-italic*** found."
        )
        checks_ok = True

    if st.button(
        "🔄 Re-run checks",
        type="primary",
        use_container_width=True,
        disabled=checks_ok,
    ):
        st.rerun()

    return checks_ok


def tailoring_update(notion: Notion, is_valid: bool):
    """Display buttons for updating resume, cover letter, and email."""
    page_descr = notion.get_descr_with_props()
    copy_text_to_file(page_descr, JOB_DESCRIPTION_FILE)

    button_config = {
        "type": "primary",
        "disabled": not is_valid,
        "use_container_width": True,
    }

    auto_update = st.checkbox("Update resume automatically", key="auto_update")

    current_page_id = notion.page_data["id"]
    if (
        auto_update
        and is_valid
        and st.session_state.get("last_auto_updated_page_id") != current_page_id
    ):
        st.session_state["last_auto_updated_page_id"] = current_page_id
        with st.spinner("Auto-updating Resume..."):
            reset_git_changes(RESUME_FILES)
            aider.update_resume()
            compile_latex(RESUME_MAIN_FILE)

    if st.button("1️⃣ Update Resume", **button_config):
        reset_git_changes(RESUME_FILES)
        aider.update_resume()
        compile_latex(RESUME_MAIN_FILE)

    if st.button("2️⃣ Update Cover letter", **button_config):
        with st.status("Cover letter", expanded=True):
            reset_git_changes([COVER_LETTER_FILE])
            aider.update_cover_letter()
            compile_latex(COVER_LETTER_FILE)


def tailoring_conclusion(notion: Notion):
    """Display button for updating applied status and uploading resume."""
    st.header("Applying")

    if st.button(
        "✅ Notion: Set Applied & Upload Resume",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("Uploading and updating status..."):
            file_id = notion.upload_pdf_resume()
            notion.set_applied_and_date(file_id=file_id)
        st.success("Successfully set as applied and uploaded resume!")


def tailoring_pdf_preview():
    """Display Resume and Cover Letter PDF previews side-by-side below columns."""
    resume_path = Path(RESUME_PDF_FILE)
    cover_path = Path(COVER_LETTER_PDF_FILE)

    if not resume_path.exists() and not cover_path.exists():
        return

    st.divider()

    st.markdown(
        """
        <style>
        iframe[data-testid="stCustomComponentV1"] {
            border: 1px solid #d0d7de !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
            border-radius: 6px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_resume, col_cover = st.columns(2)

    with col_resume:
        with st.container(border=True):
            st.subheader("Resume")
            if resume_path.exists():
                pdf_viewer(
                    input=resume_path.read_bytes(),
                    width="100%",
                    zoom_level=1.25,
                    render_text=True,
                    key=f"pdf_resume_{resume_path.stat().st_mtime}",
                )
            else:
                st.info("Resume not compiled yet.")

    with col_cover:
        with st.container(border=True):
            st.subheader("Cover Letter")
            if cover_path.exists():
                pdf_viewer(
                    input=cover_path.read_bytes(),
                    width="100%",
                    zoom_level=1.25,
                    render_text=True,
                    key=f"pdf_cover_{cover_path.stat().st_mtime}",
                )
            else:
                st.info("Cover letter not compiled yet.")
