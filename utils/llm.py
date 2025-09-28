import concurrent.futures

import google.generativeai as genai
import streamlit as st
from groq import Groq
from openai import OpenAI


class Llm:
    def __init__(self):
        self.openai = OpenAI()
        self.groq = Groq()
        self.gemini = genai.GenerativeModel("gemini-2.5-flash")

    def _openai_query(self, model: str, query: str, data: str) -> list:
        """Simple LLM query.

        Prompt caching:
            Enabled automatically at 1024 tokens. Average job posting is 300-800.
            Get cached tokens with:
            `response.usage.prompt_tokens_details.cached_tokens`
        """
        response = self.openai.chat.completions.create(
            model=model,
            # Temperature not supported on o3-like models
            # temperature=0,
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
        resp = response.choices[0].message.content
        return resp

    def _gemini_query(self, query: str, data: str) -> str:
        """Simple Gemini query."""
        prompt = f"{query}\n\n###\n\n{data}"
        response = self.gemini.generate_content(prompt)
        return response.text

    def _groq_query(self, model: str, query: str, data: str) -> str:
        chat_completion = self.groq.chat.completions.create(
            model=model,
            temperature=0,
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
        return chat_completion.choices[0].message.content

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
            "req_email": "Check if an email of a recruiter is provided for asking questions regarding the position. Replace ... with the email provided. If provided return: '✅ Email proveded: ...', otherwise '➡️ Email not provided'",
        }
        reqs_out = {}
        reqs_print = """
        ┌────────────────────────────────────────────────────────────────────────────
        │ Experience requirements
        ├────────────┬───────────────────────────────────────────────────────────────
        │ Language   │ {}
        │ Student    │ {}
        │ PhD        │ {}
        │ Years      │ {}
        │ ML         │ {}
        └────────────┴───────────────────────────────────────────────────────────────

        ┌────────────────────────────────────────────────────────────────────────────
        │ Attachments
        ├───────────┬────────────────────────────────────────────────────────────────
        │ Letter    │ {}
        │ Email     │ {}
        └───────────┴────────────────────────────────────────────────────────────────
        """
        txt_box = st.code(
            reqs_print.format("...", "...", "...", "...", "...", "...", "..."),
            language="plaintext",
        )

        def fetch_requirement(req_name, req_desc, page_content):
            # gpt-4.1-mini
            return req_name, self._gemini_query(req_desc, page_content)

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

        txt_box.code(
            reqs_print.format(
                reqs_out["req_lang"],
                reqs_out["req_stud"],
                reqs_out["req_phd"],
                reqs_out["req_years"],
                reqs_out["req_ml"],
                reqs_out["req_letter"],
                reqs_out["req_email"],
            )
        )

    def query_page_descr(self, page_descr: str) -> str:
        """Fix markdown syntax with LLM."""
        page_descr_new = self._groq_query(
            "llama-3.3-70b-versatile",
            r"""
            Check if the markdown syntax is correct. If not, fix it.
            Remove all **bold** and *italic* formatting.
            Output only the markdown.
            Syntax:
                - if there is a list, use '-' instead of '*'.
                - do not use html tags like '<br/>'.
                - never use leading spaces in the beginning of the line.
                - preserve line breaks as in the original text, including double line breaks (\n\n).
            """,
            page_descr,
        )
        return page_descr_new
