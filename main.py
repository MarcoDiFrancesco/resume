from utils.utils import (
    files_exist,
    reset_git_changes,
)
from utils.notion import Notion
from utils.llm import Llm
from utils.aider import Aider
import os
from utils.utils import (
    browser_open_silent,
    files_exist,
    copy_text_to_file,
    print_page_location_info,
    page_is_underlined,
)
from time import sleep
import streamlit as st


@st.cache_resource
def fetch_posting():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    st.markdown(
        f"📂 Notion DB: [https://notion.so/{notion.db_id}](https://notion.so/{notion.db_id})"
    )
    notion.check_db_missing_files()
    notion.fetch_page_from_db()
    notion.check_duplicate_page()
    if notion.page:
        page_descr = notion.get_descr()
        llm.fetch_requirements(page_descr)
    else:
        return

    txt_print = "📂 [Old page URL]({}) → 📂 [New page URL]({})"
    txt_box = st.markdown(txt_print.format(notion.page["url"], "..."))
    if not page_is_underlined(page_descr):
        page_descr = llm.query_page_descr(page_descr)
        notion_page_new = notion.new_page(page_descr)
        txt_box.markdown(txt_print.format(notion.page["url"], notion_page_new["url"]))
        notion.delete_page()
        notion.page = notion_page_new
    else:
        txt_box.markdown("📂 [Page URL]({}) (unchanged)".format(notion.page["url"]))
    return notion


def open_browser(notion):
    st.header("Notion - Open pages")
    if st.button("[🌐] Open Notion and LinkedIn pages", disabled=not notion):
        notion_url = notion.page["url"]
        linkedin_url = notion.page["properties"]["URL"]["url"]
        browser_open_silent(linkedin_url)
        browser_open_silent(notion_url)


def update_files(notion: Notion):
    aider = Aider()
    st.header("Aider - Update files")
    check_pass = notion.check_page_properties()

    if check_pass:
        files_exist(["JOB_DESCRIPTION.md"])
        page_descr = notion.get_descr()
        copy_text_to_file(page_descr, "JOB_DESCRIPTION.md")

        # Print City, My address, My phone number
        print_page_location_info(notion.page)

        reset_git_changes("resume.tex")
        reset_git_changes("coverletter.tex")
        reset_git_changes("header.tex")
        reset_git_changes("EMAIL_DRAFT.md")


    if st.button("Update resume", disabled=not check_pass):
        with st.expander("Resume", expanded=True):
            aider.update_header()
            aider.update_resume()
            notion.set_applied()

    if st.button("Update cover letter", disabled=not check_pass):
        with st.expander("Cover letter", expanded=True):
            aider.update_cover_letter()

    if st.button("Update email", disabled=not check_pass):
        with st.expander("Email", expanded=True):
            aider.update_email()


def main():
    notion = fetch_posting()
    open_browser(notion)
    update_files(notion)


if __name__ == "__main__":
    main()
