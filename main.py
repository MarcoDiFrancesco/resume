import os

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


from app.utils import posting, tailoring
from app.utils.notion import Notion


def main():
    st.set_page_config(page_title="Resume", layout="wide")

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.header("Posting")
        posting.posting_buttons()

        notion = posting.posting_fetch()
        if posting.posting_check(notion):
            posting.posting_info(notion)
            posting.posting_requirements(notion)
            posting.posting_fix_markdown(notion)

    with right_col:
        st.header("Tailoring")
        if notion and notion.page:
            tailoring.tailoring_links(notion)
            is_valid = tailoring.tailoring_check(notion)
            tailoring.tailoring_update(notion, is_valid)
            tailoring.tailoring_conclusion(notion)
        else:
            st.info("No active posting. Add new postings to Notion DB.")


if __name__ == "__main__":
    main()
