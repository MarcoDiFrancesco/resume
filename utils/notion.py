from notion_client import Client
import os
import datetime
from datetime import timedelta
from notion2md.exporter.block import StringExporter
from utils.utils import check_page_content
from utils.utils import get_my_address


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
        """Fetch all postings 'Not Applied' and return the first one.
        Return first all the non-senior positions.
        """
        print("[Notion] Fetching postings...", end="\r")
        query = self._query_db(
            filter={
                "property": "Stage",
                "select": {"equals": "Not Applied"},
            },
            sorts=[
                {
                    "property": "Senior position",
                    "direction": "ascending",
                }
            ],
        )
        if len(query["results"]) == 0:
            return None
        next_posting = query["results"][0]
        print(f"[Notion] Fetched {len(query["results"])} postings.  ")
        return next_posting

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
        print(f"[Notion] Check successful. Posting has no duplicates.")

    def check_db_missing_files(self) -> None:
        """Check if DB contains pages which are 'Applied' but contain no documents."""
        print("[Notion] Checking missing files in posts...", end="\r")
        query = self._query_db(
            filter={
                "and": [
                    {
                        "property": "Stage",
                        "select": {"equals": "Applied"},
                    },
                    {
                        "property": "Resume / Cover Letter",
                        "files": {"is_empty": True},
                    },
                ]
            },
        )
        # Check if there is more than one page
        if len(query["results"]) != 0:
            err_str = "[Notion] Check unsuccessful. These pages are maked as 'Applied' but have no uploaded document:\n"
            for page in query["results"]:
                err_str += f"  - {page['url']}\n"
            raise ValueError(err_str)
        print("[Notion] Check missing files in posts successful.")

    def check_page_properties(self, notion_page) -> None:
        """
        Check the following properties:
        - City: if label is non-empty
        - Role: if role is non-empty

        Note for devs:
        - Company: not checked company since ['Company']['relation'] is always empty.
        """

        def _check_property_city(notion_page):
            if not notion_page["properties"]["City"]["select"]:
                print(f"[📑] Check failed. Property 'City' is empty.")
                return False
            return True

        def _check_property_role(notion_page):
            if not notion_page["properties"]["Role"]["select"]:
                print(f"[📑] Check failed. Property 'Role' is empty.")
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
                    _check_property_role(notion_page),
                ]
            ):
                break
            input(f"[📑] Update properties and press Enter...")
        return notion_page

    def get_page_descr(self, notion_page):
        return StringExporter(block_id=notion_page["id"]).export()

    def get_page_full_content(self, notion_page) -> str:
        """Returns Notion page in markdown. Includes both properties and body.

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
        res = "# Job Properties\n"
        title = "".join(notion_page["properties"]["Position"]["title"][0]["plain_text"])
        res += f"Title: {title}\n"
        city = notion_page["properties"]["City"]["select"]["name"]
        res += f"City: {city}\n"
        my_address = get_my_address(notion_page)
        res += f"My Address: {my_address}\n"
        res += "===\n"
        res += "# Job Description\n"
        res += self.get_page_descr(notion_page)

        while not check_page_content(res):
            input(
                "[🖊] Underline check faliled. Underline text in italic-bold in Notion page. When done press Enter..."
            )
            res = self.get_page_full_content(notion_page)

        return res

    def set_date_and_applied(self, notion_page) -> None:
        date = (datetime.datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d")
        print(f"[Notion] Setting page to 'Applied' and date to '{date}'...", end="\r")
        # If time is before 6am, consider the application date as the previous day
        self.notion.pages.update(
            page_id=notion_page["id"],
            properties={
                "Stage": {"select": {"name": "Applied"}},
                "_Day": {"date": {"start": date}},
            },
        )
        print(f"[Notion] Page set to 'Applied' and date to '{date}'.      ")
