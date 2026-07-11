import os

import streamlit as st

from app.config import RESUME_MAIN_FILE
from app.utils.llm import Llm
from app.utils.notion import Notion
from app.utils.helpers import (
    files_exist,
    page_is_underlined,
)


@st.cache_resource
def fetch_posting():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    files_exist([RESUME_MAIN_FILE])
    notion.check_db_missing_files()
    notion.fetch_page_from_db()
    notion.check_duplicate_page()
    page_descr = notion.get_descr()
    llm.fetch_requirements(page_descr)

    with st.expander("Markdown fix with LLM", icon="🗣️"):
        txt_print = "📂 [Old Notion page]({}) → 📂 [New Notion page]({})"
        txt_box = st.markdown(txt_print.format(notion.page["url"], "..."))
        # Skip LLM rewrite if page was already underlined by me
        if not page_is_underlined(page_descr):
            page_descr_new = llm.query_page_descr(page_descr)
            c1, c2 = st.columns([1, 1])
            with c1:
                st.text("📝 Old description")
                st.code(page_descr, wrap_lines=True)
            with c2:
                st.text("📝 New description")
                st.code(page_descr_new, wrap_lines=True)

            notion_page_new = notion.new_page(page_descr_new)
            txt_box.markdown(
                txt_print.format(notion.page["url"], notion_page_new["url"])
            )
            notion.delete_page()
            notion.page = notion_page_new
        else:
            txt_box.markdown(
                "📂 [Notion page]({}) (text in bold italic found, left unchanged)".format(
                    notion.page["url"]
                )
            )
    return notion


def clean_all_pages_md():
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


def find_all_duplicates():
    """Find duplicates for all 'Not Applied' pages in the Notion database."""
    notion = Notion(os.environ["NOTION_DB_ID"])

    pages = notion.get_all_pages()
    st.info(f"Found {len(pages)} pages to check for duplicates.")
    progress_bar = st.progress(0)

    for i, page in enumerate(pages):
        notion.page = page
        try:
            notion.check_duplicate_page()
        except ValueError:
            # Error is already displayed by check_duplicate_page
            st.error(f"Duplicate check failed for a page. See details above.")
            return
        progress_bar.progress((i + 1) / len(pages))
    st.success("No duplicates found among 'Not Applied' pages.")
