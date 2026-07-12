import datetime
import os
from datetime import timedelta

import dateutil.parser
import httpx
import streamlit as st
from md2notionpage import core
from notion2md.exporter.block import StringExporter
from notion_client import Client

from app.config import NOTION_PAGE_SIZE
from app.utils.helpers import page_is_underlined


class Notion:
    def __init__(self, db_id: str):
        self.notion = Client(auth=os.environ["NOTION_API_TOKEN"])
        self.db_id = db_id
        self.page: dict | None = None
        self.remaining_count = 0

    @property
    def page_data(self) -> dict:
        """Returns page data, strictly typed as a dict to satisfy mypy."""
        if self.page is None:
            raise RuntimeError(
                "Attempted to access Notion page data before loading it."
            )
        return self.page

    def _query_db(self, **kwargs) -> dict:
        # database_id may be provided to be external
        if "database_id" not in kwargs:
            kwargs["database_id"] = self.db_id

        query = self.notion.databases.query(page_size=NOTION_PAGE_SIZE, **kwargs)
        if isinstance(query, dict):
            return query
        raise TypeError("Notion API query did not return a dictionary")

    def get_all_pages(self):
        """Fetch the first 25 pages from the database."""
        query = self._query_db(
            filter={
                "and": [
                    {"property": "Stage", "select": {"equals": "Not Applied"}},
                    {"property": "Unsolicited", "checkbox": {"equals": False}},
                ]
            },
        )
        return query["results"]

    def fetch_page_from_db(self) -> bool:
        """Fetch 'Not Applied' posting.

        Priority:
            1. Posting with city specified: since underlining was probably already present
                - City is deprecated, but kept in case I'll want it in the future
            2. Newest posting first, grouped by day
                - When I used to finish up all postings 'Oldest' made sense. When applying
                  infrequently there is a better chance to apply to newest postings first.
                  For example, postings above 7 days can be discarded.
            3. Company name: replicating a random choice, but deterministic
        """
        query = self._query_db(
            filter={
                "and": [
                    {"property": "Stage", "select": {"equals": "Not Applied"}},
                    {"property": "Unsolicited", "checkbox": {"equals": False}},
                ]
            },
            sorts=[
                {"property": "City", "direction": "ascending"},
                {"property": "_Day", "direction": "descending"},
                {"property": "Company", "direction": "ascending"},
            ],
        )
        if len(query["results"]) == 0:
            self.page = None
            self.remaining_count = 0
            return False
        else:
            self.page = query["results"][0]
            self.remaining_count = len(query["results"])
            return True

    def get_page_info(self) -> dict:
        """Returns details about the fetched page for display."""
        if not self.page:
            return {}

        notion_page_time = dateutil.parser.parse(
            self.page_data["created_time"]
        ).replace(tzinfo=datetime.timezone.utc)
        time_delta = datetime.datetime.now(datetime.timezone.utc) - notion_page_time
        title = "".join(
            self.page_data["properties"]["Position"]["title"][0]["plain_text"]
        )

        if company := self.page_data["properties"]["Company"]["rich_text"]:
            company_str = company[0]["plain_text"]
        else:
            company_str = "?"

        if time_delta.days >= 2:
            time_delta_str = f"{time_delta.days} days"
        elif time_delta.days >= 1:
            time_delta_str = f"{time_delta.days} day"
        elif time_delta.seconds > 60 * 60:
            time_delta_str = f"{time_delta.seconds // (60*60)} hours"
        else:
            time_delta_str = f"{time_delta.seconds // 60} minutes"

        return {
            "title": title,
            "company": company_str,
            "age": time_delta_str,
            "remaining": self.remaining_count,
        }

    def check_duplicate_page(self) -> bool:
        """
        Check for duplicates of this posting.
        Posting is a duplicate if:
        - it has the same URL, or
        - it has the same title and company
        """
        # LinkedIn URL
        url = self.page_data["properties"]["URL"]["url"]
        if not url:
            st.error("❌ **Check failed. URL is empty.**")
            return False

        # Add or remove trailing slash
        if url[-1] == "/":
            url_ts = url[:-1]
        else:
            url_ts = url + "/"
        title = self.page_data["properties"]["Position"]["title"][0]["plain_text"]
        company = self.page_data["properties"]["Company"]["rich_text"]
        company_str = company[0]["plain_text"] if company else "COMPANY NOT SET"
        query = self._query_db(
            filter={
                "or": [
                    {"property": "URL", "url": {"equals": url}},
                    {"property": "URL", "url": {"equals": url_ts}},
                    {
                        "and": [
                            {"property": "Position", "title": {"equals": title}},
                            {
                                "property": "Company",
                                "rich_text": {"equals": company_str},
                            },
                        ]
                    },
                ]
            },
        )

        if len(query["results"]) != 1:
            err_str = "❌ **Duplicate found. Posting has duplicate with same Title+Company or same URL:**\n"
            for page in query["results"]:
                err_str += f"  - [{page['url']}]({page['url']})\n"
            st.error(err_str)
            return False
        return True

    def check_db_missing_files(self) -> bool:
        """Check if DB contains pages which are 'Applied' but contain no documents."""
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
            err_str = "❌ **No CV attached. These postings are marked as 'Applied' but have no uploaded document:**\n"
            for page in query["results"]:
                err_str += f"  - {page['url']}\n"
            st.error(err_str)
            return False
        return True

    def get_descr(self):
        response = self.notion.request(
            path=f"pages/{self.page_data['id']}/markdown", method="get"
        )
        if not isinstance(response, dict):
            raise TypeError("Notion API request did not return a dictionary")

        all_markdown = response.get("markdown", "")
        # Handle truncated or unknown blocks
        for block_id in response.get("unknown_block_ids", []):
            block_resp = self.notion.request(
                path=f"pages/{block_id}/markdown", method="get"
            )
            if not isinstance(block_resp, dict):
                continue
            if "markdown" in block_resp:
                all_markdown += "\n" + block_resp["markdown"]
        return all_markdown

    def get_descr_with_props(self) -> str:
        """Returns Notion page details in markdown. Includes both properties and body.

        Example:
        ```
        # Job Properties
        Title: Data Science Internship at Google
        Compnay: Google
        ===
        # Job Description
        ## About the job
        This is your turn to apply at...
        ```
        """
        job_title = self.page_data["properties"]["Position"]["title"][0]["plain_text"]
        job_company = self.page_data["properties"]["Company"]["rich_text"][0][
            "plain_text"
        ]
        res = "# Job Properties\n"
        res += f"Title: {job_title}\n"
        res += f"Company: {job_company}\n"
        res += "===\n"
        res += "# Job Description\n"
        res += self.get_descr()
        return res

    def new_page(self, page_descr):
        """
        Create a copy of the current Notion page, overwriting page description.

        Args:
            page_descr: Page description in markdown
        """
        try:
            page_descr_blocks = core.parse_md(page_descr)
        except KeyError:
            st.code(page_descr)
            raise KeyError(
                "[❌] LLM - Prompt output with incorrect formatting. Check prompt above."
            )
        title = self.page_data["properties"]["Position"]["title"][0]["plain_text"]
        stage = self.page_data["properties"]["Stage"]["select"]["name"]
        url = self.page_data["properties"]["URL"]["url"]
        date = self.page_data["properties"]["_Day"]["date"]["start"]
        properties = {
            "Position": {"title": [{"text": {"content": title}}]},
            "Stage": {"select": {"name": stage}},
            "URL": {"url": url},
            "_Day": {"date": {"start": date}},
        }
        if company := self.page_data["properties"]["Company"]["rich_text"]:
            properties["Company"] = {
                "rich_text": [{"text": {"content": company[0]["plain_text"]}}]
            }
        # Deprecated, but kept in case I'll reuse it in the future
        if city := self.page_data["properties"]["City"]["select"]:
            properties["City"] = {"select": {"name": city["name"]}}

        notion_page = self.notion.pages.create(
            parent={"database_id": self.db_id},
            properties=properties,
            children=page_descr_blocks,
            icon={"emoji": "💼"},
        )
        return notion_page

    def delete_page(self) -> None:
        """Move notion from database to trash."""
        self.notion.pages.update(
            page_id=self.page_data["id"],
            archived=True,
        )
        self.page = None

    def upload_pdf_resume(self) -> str:
        """Upload the generated PDF resume using Notion's file upload API (2026-03-11)."""
        txt_box = st.text("[📑] Uploading resume to Notion...")
        token = os.environ["NOTION_API_TOKEN"]

        # 1. Create file upload
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2026-03-11",
            "Content-Type": "application/json",
        }
        res = httpx.post(
            "https://api.notion.com/v1/file_uploads",
            headers=headers,
            json={
                "mode": "single_part",
                "filename": "resume.pdf",
                "content_type": "application/pdf",
            },
        )
        res.raise_for_status()

        file_id = res.json()["id"]

        # 2. Upload file contents
        with open("latex/build/resume.pdf", "rb") as f:
            send_headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2026-03-11",
            }
            send_res = httpx.post(
                f"https://api.notion.com/v1/file_uploads/{file_id}/send",
                headers=send_headers,
                files={"file": ("resume.pdf", f, "application/pdf")},
            )
            send_res.raise_for_status()

        txt_box.text("[📑] Resume uploaded successfully.")
        return file_id

    def set_applied_and_date(self, file_id: str) -> None:
        txt_box = st.text(f"[📑] Setting page to 'Applied'...")
        # If time is before 6am set as previous day
        date = (datetime.datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d")

        properties = {
            "Stage": {"select": {"name": "Applied"}},
            "_Day": {"date": {"start": date}},
            "Files": {
                "files": [{"type": "file_upload", "file_upload": {"id": file_id}}]
            },
        }

        self.notion.pages.update(
            page_id=self.page_data["id"],
            properties=properties,
        )
        txt_box.text(f"[📑] Page set to 'Applied'.      ")
