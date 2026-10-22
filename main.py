import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.utils import posting, tailoring


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
            # Not checking anymore for bold-italic. Now it is now optional.
            # TODO: In the future remove the 'is_valid' check
            is_valid = tailoring.tailoring_check(notion)
            is_valid = True
            tailoring.tailoring_update(notion, is_valid)
            tailoring.tailoring_conclusion(notion)
        else:
            st.info("No active posting. Add new postings to Notion DB.")

    tailoring.tailoring_pdf_preview()


if __name__ == "__main__":
    main()
