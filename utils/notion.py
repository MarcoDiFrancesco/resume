from notion_client import Client
import os
import datetime


class Notion:
    def __init__(self, db_id: str):
        self.notion = Client(auth=os.environ["NOTION_API_TOKEN"])
        self.db_id = db_id

    def query(self, **kwargs):
        query = self.notion.databases.query(
            database_id=self.db_id, page_size=10, **kwargs
        )
        return query

    def next_posting(self):
        print("    Notion - Fetching non-applied postings from DB")
        query = self.query(
            filter={
                "property": "Stage",
                "select": {"equals": "Not Applied"},
            }
        )
        if len(query) == 0:
            return None
        next_posting = query["results"][0]
        link = next_posting["url"]
        print(f"    Notion - Fetched {len(query)} postings. Next: {link}")
        return next_posting
