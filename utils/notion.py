from notion_client import Client
import os
import datetime
from notion2md.exporter.block import StringExporter


class Notion:
    def __init__(self, db_id: str):
        self.notion = Client(auth=os.environ["NOTION_API_TOKEN"])
        self.db_id = db_id

    def _query_db(self, **kwargs):
        query = self.notion.databases.query(
            database_id=self.db_id, page_size=10, **kwargs
        )
        return query

    def _query_blocks(self, **kwargs):
        query = self.notion.blocks.children.list(**kwargs)
        return query

    def next_posting(self):
        """Fetch all postings 'Not Applied' and return the first one."""
        print("[Notion] Fetching postings...", end="\r")
        query = self._query_db(
            filter={
                "property": "Stage",
                "select": {"equals": "Not Applied"},
            }
        )
        if len(query) == 0:
            return None
        next_posting = query["results"][0]
        link = next_posting["url"]
        print(f"[Notion] Fetched {len(query)} postings. Next: {link}")
        return next_posting

    def check_duplicate_page(self, url: str) -> None:
        """
        Check if there are other postings with the same URL in the database.
        Test with and without trailing slash.

        Example:
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

    def _check_property_city(self, notion_page):
        if not notion_page["properties"]["City"]["select"]:
            print(f"[📑] Check failed. Property 'City' is empty.")
            return False
        return True

    def _check_property_role(self, notion_page):
        if not notion_page["properties"]["Role"]["select"]:
            print(f"[📑] Check failed. Property 'Role' is empty.")
            return False
        return True

    def _check_property_day(self, notion_page):
        """Check if property '_Day' is non-empty and we are applying today."""
        if not notion_page["properties"]["_Day"]["date"]:
            print(f"[📑] Check failed. Property '_Day' is empty.")
            return False
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if notion_page["properties"]["_Day"]["date"]["start"] != today:
            print(f"[📑] Check failed. Property '_Day' is not today.")
            return False
        return True

    def check_properties(self, notion_page) -> None:
        """
        Check the following properties:
        - City: if label is non-empty
        - Role: if role is non-empty
        - Day: if day is today
        - (Company: not checked company since ['Company']['relation'] is always empty.)
        """
        while [
            self._check_property_city(notion_page),
            self._check_property_role(notion_page),
            self._check_property_day(notion_page),
        ] != [True, True, True]:
            input(f"[📑] Update properties and press Enter...")
            query = self._query_db(id=notion_page["id"])
            notion_page = query["results"][0]

    def get_page_content(self, notion_page) -> str:
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
        res += "===\n"
        res += "# Job Description\n"
        res += StringExporter(block_id=notion_page["id"]).export()
        return res
