import os

import streamlit as st

from utils.aider import Aider
from utils.llm import Llm
from utils.notion import Notion
from utils.utils import (
    browser_open_silent,
    copy_text_to_file,
    files_exist,
    page_is_underlined,
    print_page_location_info,
    reset_git_changes,
)


@st.cache_resource
def fetch_posting():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    st.markdown(f"📂 [Notion DB](https://notion.so/{notion.db_id})")
    files_exist(["resume.tex"])
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
            page_descr = llm.query_page_descr(page_descr)
            notion_page_new = notion.new_page(page_descr)
            txt_box.markdown(
                txt_print.format(notion.page["url"], notion_page_new["url"])
            )
            notion.delete_page()
            notion.page = notion_page_new
        else:
            txt_box.markdown(
                "📂 [Notion page]({}) (unchanged)".format(notion.page["url"])
            )
        return notion


def open_browser(notion):
    if st.button("🌐 Open Notion and LinkedIn pages", disabled=not notion):
        notion_url = notion.page["url"]
        linkedin_url = notion.page["properties"]["URL"]["url"]
        browser_open_silent(linkedin_url)
        browser_open_silent(notion_url)


def update_files(notion: Notion):
    aider = Aider()
    check_pass = notion.check_page_properties()

    if check_pass:
        page_descr = notion.get_descr_with_props()
        copy_text_to_file(page_descr, "JOB_DESCRIPTION.md")

        # Print City, My address, My phone number
        print_page_location_info(notion.page)

    if st.button("Update Resume", disabled=not check_pass):
        with st.status("Resume", expanded=True):
            reset_git_changes("header.tex")
            reset_git_changes("resume.tex")
            aider.update_header()
            aider.update_resume()
            notion.set_applied_and_date()

    if st.button("Update Cover letter", disabled=not check_pass):
        with st.status("Cover letter", expanded=True):
            reset_git_changes("coverletter.tex")
            aider.update_cover_letter()

    if st.button("Update Email", disabled=not check_pass):
        with st.status("Email", expanded=True):
            reset_git_changes("EMAIL_DRAFT.md")
            aider.update_email()


def main():
    st.set_page_config(layout="wide")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.header("Job posting info")
        notion = fetch_posting()
    with c2:
        st.header("Update CV/Cover Letter")
        open_browser(notion)
        update_files(notion)


if __name__ == "__main__":
    main()
