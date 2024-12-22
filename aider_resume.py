from utils.utils import (
    check_files_existance,
    has_git_changes,
)
from utils.notion import Notion
from utils.llm import Llm
from utils.aider_refactor import Aider
import os
import pdb


def main():
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    # Import job posting from LinkedIn
    # while notion_page := notion.next_posting():
    notion_page = notion.next_posting()

    # Notion - Check if job positing was already in DB
    print("    Notion - Checks for duplicates")
    #   - Filter by title (without traling spaces) and link (without trailing /)
    # query = notion.query()
    # if len(query["results"]) > 0:
    #     print("Job posting already in Notion DB")
    print("    Notion - Checks finished")

    input("  Underline notion page. When done press Enter...")

    # Notion - Checking if posting contains: company, city
    print("    Notion - Checking if posting contains: company, city")
    # TODO: Implement
    print("    Notion - Checks finished")

    input(
        "  Copy notion page to JOB_DESCRIPTION.md: company, city + job description? When done press Enter..."
    )

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
    print("============================= Job posting done =============================")
    print()

main()
