from utils.utils import (
    get_links_from_file,
    check_files_existance,
    check_git_changes,
    has_job_description,
)
from utils.selenium import Selenium
from utils.notion import Notion
from utils.llm import Llm
from utils.aider_refactor import Aider
import os
import pdb


def main():
    links = get_links_from_file("JOB_POSTING_LINKS.txt")

    selenium = Selenium()
    notion = Notion(os.environ["NOTION_DB_ID"])
    llm = Llm()

    # Import job posting from LinkedIn
    for link in links:
        # Selenium - Get job posting info
        print("Selenium - Opening link:", link)
        selenium.get(link)
        input("Selenium - Did the page load? If so press Enter...")
        title = selenium.get_title()
        company_name = selenium.get_company()
        location = selenium.get_location()
        desc_html = selenium.get_description()
        print("Selenium - Information retrieved")

        # TOREMOVE: Debug values
        # title = "DEBUG JOB - Forecasting Data Scientist"
        # company_name = "Octopus Energy"
        # location = "Munich, Bavaria, Germany"
        # desc_html = '<div class="show-more-less-html__markup show-more-less-html__markup--clamp-after-5\n            relative overflow-hidden">\n          Munich, DE<br><br>Octopus Energy UK 🇬🇧 – Data /<br><br>Full-time /<br><br>On-site<br><br> <br><br>The Energy Markets team at Octopus Energy is responsible for making sure that we always have the electricity and gas we need to support our customer demand whilst also supporting the grid to enable the Net Zero transition.<br><br>To achieve this mission across all Octopus international regions, we need to forecast the demand of each of our customers and the production of our generation assets. The Forecasting team owns the underlying models and the forecasting data platform that feeds into business operations across the international group.<br><br>We are looking for a Data Scientist to join the team - ideally someone who is skilled at data analysis, has at least some experience or familiarity with machine learning models and can grasp the commercial concepts and needs of the wider business to really add value.<br><br><strong>What you will be doing:<br><br></strong><ul><li>Building, improving and maintaining forecasting models. </li><li>Development on forecasting framework and tools.</li><li>Maintaining and automating forecasting processes, whilst building in checks and alerting.</li><li>Designing and building forecasting dashboards/ reports that cover operational processes and reporting requirements;</li><li>Standardising and rolling out forecasting models across the international markets.</li><li>Performing ad-hoc analysis.</li><li>Collaborating with Risk, Trading, Renewables, Flexibility teams and building pipelines into the wider business.<br><br><br></li></ul><strong>Who we are looking for: <br><br></strong><ul><li>Experience with Python (pandas) and SQL is essential;</li><li>Able to quickly understand commercial concepts quickly and effectively;</li><li>Team player excited at the idea of ownership across lots of different projects and tools;</li><li>Passion for driving towards Net Zero;</li><li>Drives knowledge sharing and documentation for a more effective platform;</li><li>Open to travelling to Octopus international offices;</li><li>Experience with Machine Learning, dbt, Airflow and Spark is beneficial.</li><li>Experience in the energy industry would be useful but not required.<br><br><br></li></ul>\n        </div>'

        # LLM - Refactor description HTML to Markdown
        print("LLM - Sending query")
        desc_md = llm.html_to_md(desc_html)
        print("LLM - Response received")

        # # Notion - Check if job positing was already in DB
        #   - Filter by title (without traling spaces) and link (without trailing /)
        # query = notion.query()
        # if len(query["results"]) > 0:
        #     print("Job posting already in Notion DB")

        # Notion - Add posting to DB
        print("Notion - Adding page")
        notion_page = notion.new_page(title, company_name, location, link, desc_md)
        print(f"Notion - Page added at: {notion_page["url"]}")

        # - Create new Notion page in DB copying:
        #   - name
        #   - company: if not already existing
        #   - link
        #   - description: maybe ask 4o-mini to fix readme formatting
        #   - location: check for exact match in the string locations

        input(
            "Application Submitted? If so, press Enter to process next job posting..."
        )

        # Initiate each time new LLM instance (why???)
        aider_refactor = Aider()
        check_git_changes("resume.tex")
        check_git_changes("EMAIL_DRAFT.md")
        print("✅ Resume and Email draft have no git changes")
        has_job_description()
        print("✅ Job description is not empty")
        aider_refactor.run_prompts()


main()
