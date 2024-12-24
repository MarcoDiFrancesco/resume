from utils.utils import (
    check_files_existance,
    has_git_changes,
)
from utils.notion import Notion
from utils.llm import Llm
from utils.aider_refactor import Aider
import os
from utils.utils import browser_open_silent, check_files_existance, copy_text_to_file


def main():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    notion_page = notion.next_posting()
    notion_url = notion_page["url"]
    linkedin_url = notion_page["properties"]["URL"]["url"]

    # browser_open_silent(notion_url)
    # browser_open_silent(linkedin_url)

    notion.check_duplicate_page(linkedin_url)

    # DEBUG: desabled check
    # input("[🖊] Underline notion page. When done press Enter...")

    notion.check_properties(notion_page)

    notion_page_content = notion.get_page_content(notion_page)

    check_files_existance(["JOB_DESCRIPTION.md"])
    copy_text_to_file(notion_page_content, "JOB_DESCRIPTION.md")
    print("[📂] Notion page content copied to JOB_DESCRIPTION.md")

    # LLM - Fetch requirements: German, Currenty univerity student, PhD, Cover Letter, Recruiter email
    print("    LLM: fetching requirements")
    print("    LLM: requirements fetched")

    print(
        """
        === Job posting details ===
            Title: Praticante universitario Digital Innovation / Data Science (TESTTTT)
            Page created: 3 minutes ago
            Location: Zurich
            My address: Maneggstrasse 41, 8041 Zürich, Switzerland (this address is hard-coded with a map: {"city": "address"})
            
            ❌ No requirement languge (non-English)
            ❌ No requirement Current university student
            ❌ No requirement PhD
        === Generating cover letter ===
        """
    )

    # Initiate each time new LLM instance (why???)
    aider_refactor = Aider()

    while has_git_changes("resume.tex"):
        input(
            f"  File resume.tex has git changes. Remove git changes then press Enter..."
        )

    while has_git_changes("coverletter.tex"):
        input(
            f"  File coverletter.tex has git changes. Remove git changes then press Enter..."
        )

    while has_git_changes("EMAIL_DRAFT.md"):
        input(
            f"  File EMAIL_DRAFT.tex has git changes. Remove git changes then press Enter..."
        )

    print("  Aider - Resume")
    input("          Do you want to update it? [y / n / enter(y)]:")

    aider_refactor.update_resume()

    print("  Aider - Cover letter (✅ Cover Letter required)")
    input("          Do you want to update it? [y / n / enter(y)]:")

    aider_refactor.update_cover_letter()

    print("  Aider - Email (✅ Recruiter email provided)")
    input("          Do you want to create it? [y / n / enter(y)]:")

    aider_refactor.create_email()
    print()
    print(
        "============================= Job posting done ============================="
    )
    print()


main()
