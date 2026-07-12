import concurrent.futures

import streamlit as st
from openai import OpenAI

from app.config import GEMINI_FLASH_LITE_MODEL, GEMINI_FLASH_MODEL


class Llm:
    def __init__(self):
        self.openai = OpenAI()

    def _query(self, model: str, query: str, data: str) -> str:
        """Simple LLM query using OpenAI compatible endpoint."""
        response = self.openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": query,
                },
                {
                    "role": "user",
                    "content": data,
                },
            ],
        )
        return response.choices[0].message.content

    def fetch_requirements(self, page_content: str):
        """
        Note: OpenAI JSON Mode suppressed
            Not used since even with Mono-query returned wrong result for:
                "Check if a cover letter or a motivation letter required.
                If so return True, otherwise False"
        """
        req_explain_prompt = (
            "Replace ... with this requirement details in less than 10 words."
        )
        # Requirements
        reqs_prompt = {
            "req_lang": f"Check if there are non-English languages which are STRICTLY required. {req_explain_prompt}. If so: '❌ Language: ...'. Otherwise: '➡️ Language requirement passed'",
            "req_stud": f"Check if the candidate is required to be currently enrolled at the university. {req_explain_prompt}. If required return: '❌ Student status required: ...'. Otherwise: '➡️ Current university student status requirement passed'",
            "req_phd": "Check if a PhD degree is strictly required. If so: '❌ PhD position required'. Otherwise: '➡️ PhD requirement passed'",
            "req_years": f"""
                Check if 4+ years of experience are required.
                {req_explain_prompt}
                If required:     '❌ Years of experience required: ...'
                For example:     '❌ Years of experience required: 5 years in Devops, 4 in ML'
                If not required: '➡️ Years of experience requirement passed'
            """,
            "req_ml": "Check if this position includes working with statistical models, like training or deploying machine learning models or AI models. If so: '➡️ Machine Learning included'. Otherwise: '❌ No mentions of Machine Learning'",
            "req_letter": f"Check if the cover letter or motivation letter is required. {req_explain_prompt}. If required return: '✅ Letter required: ...', otherwise '➡️ Letter not required'",
            "req_email": "Check if an email of a recruiter is provided for asking questions regarding the position. Replace ... with the email provided. If provided return: '✅ Email provided: ...', otherwise '➡️ Email not provided'",
            "req_phone": "Check if a phone number of a recruiter is provided for asking questions regarding the position. Replace ... with the phone number provided. If provided return: '✅ Phone provided: ...', otherwise '➡️ Phone not provided'",
        }
        reqs_out = {}

        def fetch_requirement(req_name, req_desc, page_content):
            return req_name, self._query(GEMINI_FLASH_MODEL, req_desc, page_content)

        # Make LLM requests in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    fetch_requirement, req_name, req_desc, page_content
                ): req_name
                for req_name, req_desc in reqs_prompt.items()
            }
            for future in concurrent.futures.as_completed(futures):
                req_name, res = future.result()
                reqs_out[req_name] = res

        st.subheader("📋 Posting Analysis")
        col1, col2 = st.columns([3, 2])

        with col1:
            st.dataframe(
                [
                    {"Category": "Language", "Status": reqs_out["req_lang"]},
                    {"Category": "Student", "Status": reqs_out["req_stud"]},
                    {"Category": "PhD", "Status": reqs_out["req_phd"]},
                    {"Category": "Years", "Status": reqs_out["req_years"]},
                    {"Category": "ML", "Status": reqs_out["req_ml"]},
                ],
                column_config={
                    "Category": st.column_config.TextColumn(None),
                    "Status": st.column_config.TextColumn(None),
                },
                hide_index=True,
                use_container_width=True,
            )

        with col2:
            st.dataframe(
                [
                    {"Category": "Letter", "Status": reqs_out["req_letter"]},
                    {"Category": "Email", "Status": reqs_out["req_email"]},
                    {"Category": "Phone", "Status": reqs_out["req_phone"]},
                ],
                column_config={
                    "Category": st.column_config.TextColumn(None),
                    "Status": st.column_config.TextColumn(None),
                },
                hide_index=True,
                use_container_width=True,
            )

    def query_page_descr(self, page_descr: str) -> str:
        """Fix markdown syntax with LLM."""
        page_descr_new = self._query(
            GEMINI_FLASH_LITE_MODEL,
            r"""
            Check if the markdown syntax is correct. If not, fix it.
            Output only the markdown.
            Syntax:
                - if there is a list, use '-' instead of '*'.
                - do not use html tags like '<br/>'.
                - do not use leading spaces in the beginning of the line.
                - do not format links in markdown, instead in plain text in square brackets, e.g. [https://linkedin.com/xyz].
                - preserve line breaks as in the original text, including double line breaks (\n\n).
                - Remove all **bold** and *italic* formatting. Then, add in h3 (with hashtags) the section headings, and **bold** the subsections.
            """,
            page_descr,
        )
        return page_descr_new
