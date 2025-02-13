from notion_client import Client
import os
import datetime
from datetime import timedelta
from notion2md.exporter.block import StringExporter
from utils.utils import page_is_underlined
from utils.utils import get_my_address
from md2notionpage import core


class Notion:
    def __init__(self, db_id: str):
        self.notion = Client(auth=os.environ["NOTION_API_TOKEN"])
        self.db_id = db_id

    def _query_db(self, **kwargs):
        query = self.notion.databases.query(
            database_id=self.db_id, page_size=25, **kwargs
        )
        return query

    def _query_blocks(self, **kwargs):
        query = self.notion.blocks.children.list(**kwargs)
        return query

    def next_posting(self):
        """Fetch 'Not Applied' postings and return first with priority.

        Priority:
            1. posting with city specified: since underlining was probably already present
            2. oldest posting first
            3. company name: replicating a random choice, but deterministic
        """
        print_string = "[📂] Notion"
        print(f"{print_string} - Fetching postings...", end="\r")
        query = self._query_db(
            filter={
                "property": "Stage",
                "select": {"equals": "Not Applied"},
            },
            sorts=[
                {
                    "property": "City",
                    "direction": "ascending",
                },
                {
                    "property": "_Day",
                    "direction": "ascending",
                },
                {
                    "property": "Company",
                    "direction": "ascending",
                },
            ],
        )
        if len(query["results"]) == 0:
            return None
        next_posting = query["results"][0]
        print(f"{print_string} - Fetched {len(query["results"])} postings   ")
        return next_posting

    def fix_page_descr(self):
        print("[📂] Notion - Fixing page description...", end="\r")
        page_descr = self.get_page_descr()

        print("[📂] Notion - Fixing page description - Successful")

    def check_duplicate_page(self, url: str) -> None:
        """
        Check for other postings with the same URL with and without trailing slash.
        If dupicate is found, raise ValueError.

        Example of same URLs:
            - https://www.linkedin.com/jobs/view/1234567890
            - https://www.linkedin.com/jobs/view/1234567890/
        """
        print("[Notion] Checking if page has duplicates...", end="\r")
        assert url, "[Notion] Check failed. URL is empty."

        # Add or remove trailing slash
        if url[-1] == "/":
            url_ts = url[:-1]
        else:
            url_ts = url + "/"

        query = self._query_db(
            filter={
                "or": [
                    {
                        "property": "URL",
                        "url": {"equals": url},
                    },
                    {
                        "property": "URL",
                        "url": {"equals": url_ts},
                    },
                ]
            }
        )

        if len(query["results"]) != 1:
            raise ValueError(f"[Notion] Check failed. Posting has duplicates: {url}")
        print(f"[📂] Notion database check - Posting has no duplicates - Successful")

    def check_db_missing_files(self) -> None:
        """Check if DB contains pages which are 'Applied' but contain no documents."""
        log_str = "[📂] Notion database check"
        print(f"{log_str} - Checking missing files in posts...", end="\r")
        query = self._query_db(
            filter={
                "and": [
                    {
                        "property": "Stage",
                        "select": {"equals": "Applied"},
                    },
                    {
                        "property": "Files",
                        "files": {"is_empty": True},
                    },
                ]
            },
        )
        # Check if there is more than one page
        if len(query["results"]) != 0:
            err_str = f"{log_str} - Check failed. These pages are maked as 'Applied' but have no uploaded document:\n"
            for page in query["results"]:
                err_str += f"  - {page['url']}\n"
            raise ValueError(err_str)
        print(f"{log_str} - Check missing files in posts - Successful")

    def check_page_properties(self, notion_page) -> None:
        """
        Check the following properties:
        - City: if label is non-empty
        - Company: if text is non-empty
        """

        def _check_property_city(notion_page):
            if not notion_page["properties"]["City"]["select"]:
                print(f"[📑] Check failed. Property 'City' is empty.")
                return False
            return True

        def _check_property_company(notion_page):
            if not notion_page["properties"]["Company"]["rich_text"]:
                print(f"[📑] Check failed. Property 'Company' is empty.")
                return False
            return True

        url = notion_page["properties"]["URL"]["url"]
        while True:
            query = self._query_db(
                filter={
                    "property": "URL",
                    "url": {"equals": url},
                }
            )
            assert len(query["results"]) == 1, "Duplicate posting with same URL."
            notion_page = query["results"][0]
            if all(
                [
                    _check_property_city(notion_page),
                    _check_property_company(notion_page),
                ]
            ):
                break
            input(f"[📑] Update properties and press Enter...")
        return notion_page

    def get_page_descr(self, notion_page):
        return StringExporter(block_id=notion_page["id"]).export()

    def new_page(self, notion_page_old, page_descr):
        """
        Copy page including title and properties
        """
        print("[📂] Notion - Writing new page...", end="\r")
        try:
            page_descr_blocks = core.parse_md(page_descr)
        except KeyError:
            print(page_descr)
            raise KeyError(
                "[❌] LLM - Prompt output with incorrect formatting. Check prompt above."
            )
        # If time is before 6am, consider the application date as the previous day
        date = (datetime.datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d")
        properties = {
            "Position": {
                "title": [
                    {
                        "text": {
                            "content": notion_page_old["properties"]["Position"][
                                "title"
                            ][0]["plain_text"]
                        }
                    }
                ]
            },
            "Stage": {
                "select": {
                    "name": notion_page_old["properties"]["Stage"]["select"]["name"]
                }
            },
            "URL": {"url": notion_page_old["properties"]["URL"]["url"]},
            "_Day": {"date": {"start": date}},
        }
        if notion_page_old["properties"]["Company"]["rich_text"]:
            properties["Company"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": notion_page_old["properties"]["Company"][
                                "rich_text"
                            ][0]["plain_text"]
                        }
                    }
                ]
            }

        if notion_page_old["properties"]["City"]["select"]:
            properties["City"] = {
                "select": {
                    "name": notion_page_old["properties"]["City"]["select"]["name"]
                }
            }

        notion_page = self.notion.pages.create(
            parent={"database_id": self.db_id},
            properties=properties,
            children=page_descr_blocks,
            icon={"emoji": "💼"},
        )
        print("[📂] Notion - Writing new page - Successful")
        return notion_page

    def delete_page(self, notion_page) -> None:
        print("[📂] Notion - Deleting old page...", end="\r")
        self.notion.pages.update(
            page_id=notion_page["id"],
            archived=True,
        )
        print("[📂] Notion - Deleting old page - Successful")

    def get_page_full_content(self, notion_page) -> str:
        """Returns Notion page details in markdown. Includes both properties and body.

        Example:
        ```
        # Job Properties
        Title: Data Science Internship at Example
        City: Zurich
        ===
        # Job Description
        ## About the job
        This is your turn to apply at...
        ```
        """
        job_title = notion_page["properties"]["Position"]["title"][0]["plain_text"]
        job_city = notion_page["properties"]["City"]["select"]["name"]
        res = "# Job Properties\n"
        res += f"Title: {job_title}\n"
        res += f"City: {job_city}\n"
        res += f"My Address: {get_my_address(notion_page)}\n\n"
        res += f"# Job Description\n"
        res += self.get_page_descr(notion_page)
        while not page_is_underlined(res):
            input(
                "[🖊] Underline check faliled. Underline text in italic-bold in Notion page. When done press Enter..."
            )
            res = self.get_page_full_content(notion_page)
        return res

    def set_applied(self, notion_page) -> None:
        print(f"[📑] Setting page to 'Applied'...", end="\r")
        self.notion.pages.update(
            page_id=notion_page["id"],
            properties={
                "Stage": {"select": {"name": "Applied"}},
            },
        )
        print(f"[📑] Page set to 'Applied'.      ")
