from utils.utils import (
    check_files_existance,
    reset_git_changes,
)
from utils.notion import Notion
from utils.llm import Llm
from utils.aider import Aider
import os
from utils.utils import (
    browser_open_silent,
    check_files_existance,
    copy_text_to_file,
    print_page_summary,
    print_page_requirements,
)


def main():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()
    aider = Aider()

    notion.check_db_missing_files()
    notion_page = notion.next_posting()
    if not notion_page:
        print("[✅] No new postings found. Add new postings to the Notion DB.")
        return
    page_descr = notion.get_page_descr(notion_page)
    requirements = llm.fetch_requirements(page_descr)
    print_page_requirements(requirements)

    notion_url = notion_page["url"]
    linkedin_url = notion_page["properties"]["URL"]["url"]
    notion.check_duplicate_page(linkedin_url)
    browser_open_silent(notion_url)
    browser_open_silent(linkedin_url)

    input("[🖊] Underline text in italic-bold in Notion page. When done press Enter...")
    notion_page = notion.check_page_properties(notion_page)
    page_full_content = notion.get_page_full_content(notion_page)

    check_files_existance(["JOB_DESCRIPTION.md"])
    copy_text_to_file(page_full_content, "JOB_DESCRIPTION.md")

    print_page_summary(notion_page)

    reset_git_changes("resume.tex")
    reset_git_changes("coverletter.tex")
    reset_git_changes("EMAIL_DRAFT.md")

    aider.update_resume()
    notion.set_date_and_applied(notion_page)
    aider.update_cover_letter()
    aider.update_email()


main()
