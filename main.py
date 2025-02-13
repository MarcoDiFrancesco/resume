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
    print_page_details,
    print_page_requirements,
    print_page_location_info,
    page_is_underlined
)
from time import sleep
import streamlit as st

def main():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()
    aider = Aider()

    notion.check_db_missing_files()
    notion_page = notion.next_posting()
    if not notion_page:
        st.tex("[📂] Notion - No new postings found. Add new postings to the Notion DB.")
        return

    print_page_details(notion_page)
    # page_descr = notion.get_page_descr(notion_page)

    # # Fix markdown formatting if page was not already underlined
    # if not page_is_underlined(page_descr):
    #     # Fix markdown formatting with LLM
    #     page_descr = llm.fix_page_descr(page_descr)
    #     # Copy markdown to new notion page
    #     notion_page_new = notion.new_page(notion_page, page_descr)
    #     # Delete old notion page
    #     notion.delete_page(notion_page)
    #     notion_page = notion_page_new

    # requirements = llm.fetch_requirements(page_descr)
    # print_page_requirements(requirements)

    # notion_url = notion_page["url"]
    # linkedin_url = notion_page["properties"]["URL"]["url"]
    # notion.check_duplicate_page(linkedin_url)
    # browser_open_silent(linkedin_url)
    # # Wait for browser to open the notion page page, otherwise it may open the linkedin page first
    # sleep(0.3)
    # browser_open_silent(notion_url)

    # input("[🖊] Underline text in bold-italic in Notion page. When done press Enter...")
    # notion_page = notion.check_page_properties(notion_page)
    # page_full_content = notion.get_page_full_content(notion_page)

    # files_exist(["JOB_DESCRIPTION.md"])
    # copy_text_to_file(page_full_content, "JOB_DESCRIPTION.md")

    # # Print City, My address, My phone number
    # print_page_location_info(notion_page)

    # reset_git_changes("resume.tex")
    # reset_git_changes("coverletter.tex")
    # reset_git_changes("header.tex")
    # reset_git_changes("EMAIL_DRAFT.md")

    # aider.update_header()
    # aider.update_resume()
    # notion.set_applied(notion_page)
    # aider.update_cover_letter()
    # aider.update_email()


if __name__ == "__main__":
    if st.button("Process new posting"):
        main()
