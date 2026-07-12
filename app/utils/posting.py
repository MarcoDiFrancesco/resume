import os

import streamlit as st

from app.config import NOTION_PURPOSE_PAGE_URL, RESUME_MAIN_FILE
from app.utils.helpers import (
    files_exist,
    page_is_underlined,
)
from app.utils.llm import Llm
from app.utils.notion import Notion


def posting_buttons():
    """Display buttons for Notion links and actions."""
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
            posting_check.clear()
            posting_fetch.clear()
            posting_info.clear()
            posting_requirements.clear()
            posting_fix_markdown.clear()
    with col2:
        if st.button("🪥 Clean Markdown pages", use_container_width=True):
            _clean_all_pages_md()
    with col3:
        if st.button("⿻ Find Duplicates", use_container_width=True):
            _find_all_duplicates()


@st.cache_resource
def posting_fetch() -> Notion:
    """Fetch the next Notion page."""
    notion = Notion(os.environ["NOTION_DB_ID"])
    notion.fetch_page_from_db()
    return notion


@st.cache_data
def posting_check(_notion: Notion) -> bool:
    """Run all pre-flight and database checks."""
    with st.status("Running pre-flight checks...", expanded=True) as status:
        if not files_exist([RESUME_MAIN_FILE]):
            st.error(f"❌ Main resume file '{RESUME_MAIN_FILE}' missing.")
            status.update(
                label="❌ Pre-flight checks failed", state="error", expanded=True
            )
            return False
        st.write(f"✅ Main resume file '{RESUME_MAIN_FILE}' found.")

        if not _notion.check_db_missing_files():
            status.update(
                label="❌ Pre-flight checks failed", state="error", expanded=True
            )
            return False
        st.write("✅ DB check: All 'Applied' postings have CVs attached.")

        if not _notion.page:
            st.warning(
                "❌ No new posting 'Non Applied' found. Add new postings to Notion DB."
            )
            status.update(
                label="❌ Pre-flight checks failed", state="error", expanded=True
            )
            return False

        if not _notion.check_duplicate_page():
            status.update(
                label="❌ Pre-flight checks failed", state="error", expanded=True
            )
            return False
        st.write("✅ DB check: No duplicates found for this posting.")

        if not _notion.page_data["properties"]["Company"]["rich_text"]:
            st.error(
                "❌ Property *Company* in Notion page is empty. Edit Notion page and fetch again."
            )
            status.update(
                label="❌ Pre-flight checks failed", state="error", expanded=True
            )
            return False
        st.write("✅ Property *Company* in Notion page found.")

        status.update(label="✅ All checks passed", state="complete", expanded=False)
        return True


@st.cache_data
def posting_info(_notion: Notion):
    """Display basic information about the fetched posting."""
    info = _notion.get_page_info()
    st.subheader(f"ℹ️ Posting ({info['remaining']} left)")
    st.dataframe(
        [
            {"Attribute": "Title", "Value": info["title"]},
            {"Attribute": "Company", "Value": info["company"]},
            {"Attribute": "Page age", "Value": info["age"]},
        ],
        column_config={
            "Attribute": st.column_config.TextColumn(None),
            "Value": st.column_config.TextColumn(None),
        },
        hide_index=True,
        use_container_width=True,
    )


@st.cache_data
def posting_requirements(_notion: Notion):
    """Fetch and display posting requirements using LLM."""
    llm = Llm()
    page_descr = _notion.get_descr()
    llm.fetch_requirements(page_descr)


@st.cache_data
def posting_fix_markdown(_notion: Notion):
    """Format and rewrite Notion page description using LLM if needed."""
    llm = Llm()
    page_descr = _notion.get_descr()

    with st.expander("Markdown fix with LLM", icon="🗣️"):
        txt_print = "📂 [Old Notion page]({}) → 📂 [New Notion page]({})"
        txt_box = st.markdown(txt_print.format(_notion.page_data["url"], "..."))

        # Skip LLM rewrite if page is already ***underlined***
        if page_is_underlined(page_descr):
            txt_box.markdown(
                "📂 [Notion page]({}) (text in bold italic found, left unchanged)".format(
                    _notion.page_data["url"]
                )
            )
        else:
            page_descr_new = llm.query_page_descr(page_descr)
            c1, c2 = st.columns([1, 1])
            with c1:
                st.text("📝 Old description")
                st.code(page_descr, wrap_lines=True)
            with c2:
                st.text("📝 New description")
                st.code(page_descr_new, wrap_lines=True)

            notion_page_new = _notion.new_page(page_descr_new)
            txt_box.markdown(
                txt_print.format(_notion.page_data["url"], notion_page_new["url"])
            )
            _notion.delete_page()
            _notion.page = notion_page_new


def _clean_all_pages_md():
    """Clean markdown for all pages in the Notion database."""
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    pages = notion.get_all_pages()
    st.info(f"Found {len(pages)} pages to process.")
    progress_bar = st.progress(0)

    for i, page in enumerate(pages):
        notion.page = page
        page_descr = notion.get_descr()

        if not page_is_underlined(page_descr):
            page_descr_new = llm.query_page_descr(page_descr)
            notion.new_page(page_descr_new)
            notion.delete_page()
        progress_bar.progress((i + 1) / len(pages))
    st.success("All pages have been processed.")


def _find_all_duplicates():
    """Find duplicates for all 'Not Applied' pages in the Notion database."""
    notion = Notion(os.environ["NOTION_DB_ID"])

    pages = notion.get_all_pages()
    st.info(f"Found {len(pages)} pages to check for duplicates.")
    progress_bar = st.progress(0)

    for i, page in enumerate(pages):
        notion.page = page
        notion.check_duplicate_page()
        progress_bar.progress((i + 1) / len(pages))
    st.success("Duplicate check completed for 'Not Applied' pages.")
