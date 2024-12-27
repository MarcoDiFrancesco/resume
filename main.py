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
)


def main():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()
    aider_resume = Aider()

    notion.check_db_errors()

    notion_page = notion.next_posting()
    notion_url = notion_page["url"]
    linkedin_url = notion_page["properties"]["URL"]["url"]

    browser_open_silent(notion_url)
    browser_open_silent(linkedin_url)

    notion.check_duplicate_page(linkedin_url)

    input("[🖊] Underline text in italic-bold in Notion page. When done press Enter...")
    notion_page = notion.check_properties(notion_page)
    page_content = notion.get_page_content(notion_page)

    check_files_existance(["JOB_DESCRIPTION.md"])
    copy_text_to_file(page_content, "JOB_DESCRIPTION.md")

    requirements = llm.fetch_requirements(page_content)
    print_page_summary(notion_page, requirements)

    reset_git_changes("resume.tex")
    reset_git_changes("coverletter.tex")
    reset_git_changes("EMAIL_DRAFT.md")

    aider_resume.update_resume()
    aider_resume.update_resume_address()
    aider_resume.update_cover_letter()
    aider_resume.create_email()

    notion.set_to_applied(notion_page)


main()
