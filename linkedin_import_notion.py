from notion_client import Client
import os
import datetime


class Notion:
    def __init__(self, db_id: str):
        self.notion = Client(auth=os.environ["NOTION_API_TOKEN"])
        self.db_id = db_id

    def query(self, **kwargs):
        # TODO: fix the filter. I'm unable to create a working filter....
        query = self.notion.databases.query(
            database_id=self.db_id,
            page_size=5,
            filter={
                "title": {
                    # "property": "Position",
                    "equals": "Machine Learning Engineer"
                },
            },
        )
        return query

    def new_page(
        self,
        title: str,
        company_name: str,
        location: str,
        link: str,
        desc_md: list[str],
    ):
        desc_blocks = []
        for line in desc_md:
            desc_blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    # "paragraph": {
                    #     "text": [{"type": "text", "text": {"content": line}}],
                    # },
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line},
                            }
                        ],
                    },
                }
            )

        page = self.notion.pages.create(
            parent={"database_id": self.db_id},
            icon={"type": "emoji", "emoji": "💼"},
            properties={
                "Position": {"title": [{"text": {"content": title}}]},
                # "Company": {"relation": ...},
                # "City": {"select": {"name": "Munich"}},
                # "Role": {"select": {"name": "Data Scientist"}},
                "Stage": {"select": {"name": "Not Applied"}},
                "URL": {"url": link},
                "_Day": {"date": {"start": datetime.date.today().isoformat()}},
            },
            children=desc_blocks,
        )
        return page
