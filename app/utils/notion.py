import datetime
import os
from datetime import timedelta

import dateutil
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

    def _query_db(self, **kwargs):
        # database_id may be provided to be external
        if "database_id" not in kwargs:
            kwargs["database_id"] = self.db_id

        query = self.notion.databases.query(page_size=NOTION_PAGE_SIZE, **kwargs)
        return query

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
        txt_print = """
        ┌────────────────────────────────────────────────────────────────────────────
        │ Posting ({} left)
        ├────────────┬───────────────────────────────────────────────────────────────
        │ Title      │ {}
        │ Company    │ {}
        │ Page age   │ {}
        └────────────┴───────────────────────────────────────────────────────────────
        """
        txt_box = st.code(txt_print.format("...", "...", "...", "..."))
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
            txt_box.write(
                "⬆️ No new posting 'Non Applied' found. Add new postings to Notion DB."
            )
            st.warning(
                "❌ No new posting 'Non Applied' found. Add new postings to Notion DB."
            )
            return False
        else:
            self.page = query["results"][0]
            notion_page_time = dateutil.parser.parse(self.page["created_time"]).replace(
                tzinfo=datetime.timezone.utc
            )
            # Notion page age
            # TODO: set the page age to resetting at midnight, e.g. adding post at 22:00,
            #       the following day seeting at 10:00 it's anyway 1 day old
            time_delta = datetime.datetime.now(datetime.timezone.utc) - notion_page_time
            title = "".join(
                self.page["properties"]["Position"]["title"][0]["plain_text"]
            )
            if company := self.page["properties"]["Company"]["rich_text"]:
                company = company[0]["plain_text"]
            else:
                company = "?"
            if time_delta.days >= 2:
                time_delta_str = f"{time_delta.days} days"
            if time_delta.days >= 1:
                time_delta_str = f"{time_delta.days} day"
            elif time_delta.seconds > 60 * 60:
                time_delta_str = f"{time_delta.seconds // (60*60)} hours"
            else:
                time_delta_str = f"{time_delta.seconds // 60} minutes"

            txt_box.code(
                txt_print.format(len(query["results"]), title, company, time_delta_str)
            )
            return True

    def check_duplicate_page(self) -> bool:
        """
        Check for duplicates of this posting.
        Posting is a duplicate if:
        - it has the same URL, or
        - it has the same title and company
        """

        # LinkedIn URL
        url = self.page["properties"]["URL"]["url"]
        assert url, "[Notion] Check failed. URL is empty."

        # Add or remove trailing slash
        if url[-1] == "/":
            url_ts = url[:-1]
        else:
            url_ts = url + "/"
        title = self.page["properties"]["Position"]["title"][0]["plain_text"]
        company = self.page["properties"]["Company"]["rich_text"]
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
            st.warning(err_str)
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
            err_str = "[📂] **No CV attached. These postings are marked as 'Applied' but have no uploaded document:**\n"
            for page in query["results"]:
                err_str += f"  - {page['url']}\n"
            st.warning(err_str)
            return False
        return True

    def check_page_properties(self) -> bool:
        """
        Check the following properties:
        - City: if label is non-empty
        - Company: if text is non-empty
        """

        # def _check_property_city():
        #     if not self.page["properties"]["City"]["select"]:
        #         st.markdown(
        #             f"📑 Property *City* in [Notion page]({self.page['url']}) is empty → Reload Streamlit page to check again"
        #         )
        #         return False
        #     return True

        def _check_property_company():
            err_message = st.empty()
            if not self.page["properties"]["Company"]["rich_text"]:
                err_message.markdown(
                    f"📑 Property *Company* in Notion page is empty → Edit Notion page and rerun checks"
                )
                return False
            else:
                err_message.markdown("✅ Property *Company* in Notion page found.")
                return True

        def _check_page_underlined():
            err_message = st.empty()
            if not page_is_underlined(self.get_descr()):
                err_message.markdown(
                    f"❌ Highlighting of Notion page in ***bold-italic*** not found → Edit Notion page and rerun checks"
                )
                return False
            else:
                err_message.markdown(
                    "✅ Highlighting of Notion page in ***bold-italic*** found."
                )
                return True

        url = self.page["properties"]["URL"]["url"]

        query = self._query_db(
            filter={
                "property": "URL",
                "url": {"equals": url},
            }
        )
        if len(query["results"]) > 1:
            st.error("Duplicate posting with same URL.")
            return False
        self.page = query["results"][0]
        st.subheader("Checks")
        checks_ok = all(
            [
                # _check_property_city(), # Deprecated, not setting working city anymore
                _check_property_company(),
                _check_page_underlined(),
            ]
        )
        if st.button(
            "🔄 Re-run checks",
            type="primary",
            use_container_width=True,
            disabled=checks_ok,
        ):
            st.rerun()

        return checks_ok

    # def get_descr(self):
    #     print("=====", self.page)
    #     print("-----", StringExporter(block_id=self.page["id"]).export())
    #     return StringExporter(block_id=self.page["id"]).export()

    def get_descr(self):
        response = self.notion.request(
            path=f"pages/{self.page['id']}/markdown", method="get"
        )
        all_markdown = response.get("markdown", "")
        # Handle truncated or unknown blocks
        for block_id in response.get("unknown_block_ids", []):
            block_resp = self.notion.request(
                path=f"pages/{block_id}/markdown", method="get"
            )
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
        job_title = self.page["properties"]["Position"]["title"][0]["plain_text"]
        job_company = self.page["properties"]["Company"]["rich_text"][0]["plain_text"]
        res = "# Job Properties\n"
        res += f"Title: {job_title}\n"
        res += f"Company: {job_company}\n"
        res += f"==="
        res += f"# Job Description\n"
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
        title = self.page["properties"]["Position"]["title"][0]["plain_text"]
        stage = self.page["properties"]["Stage"]["select"]["name"]
        url = self.page["properties"]["URL"]["url"]
        date = self.page["properties"]["_Day"]["date"]["start"]
        properties = {
            "Position": {"title": [{"text": {"content": title}}]},
            "Stage": {"select": {"name": stage}},
            "URL": {"url": url},
            "_Day": {"date": {"start": date}},
        }
        if company := self.page["properties"]["Company"]["rich_text"]:
            properties["Company"] = {
                "rich_text": [{"text": {"content": company[0]["plain_text"]}}]
            }
        # Deprecated, but kept in case I'll reuse it in the future
        if city := self.page["properties"]["City"]["select"]:
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
            page_id=self.page["id"],
            archived=True,
        )
        self.page = None

    def set_applied_and_date(self) -> None:
        txt_box = st.text(f"[📑] Setting page to 'Applied'...")
        # If time is before 6am set as previous day
        date = (datetime.datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d")
        self.notion.pages.update(
            page_id=self.page["id"],
            properties={
                "Stage": {"select": {"name": "Applied"}},
                "_Day": {"date": {"start": date}},
            },
        )
        txt_box.text(f"[📑] Page set to 'Applied'.      ")
