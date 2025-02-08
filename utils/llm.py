from openai import OpenAI
from groq import Groq
import concurrent.futures


class Llm:
    def __init__(self):
        self.openai = OpenAI()
        self.groq = Groq()

    def _openai_query(self, model: str, query: str, data: str) -> list:
        """Simple LLM query.

        Prompt caching:
            Enabled automatically at 1024 tokens. Average job posting is 300-800.
            Get cached tokens with:
            `response.usage.prompt_tokens_details.cached_tokens`
        """
        response = self.openai.chat.completions.create(
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
        resp = response.choices[0].message.content
        return resp

    def _groq_query(self, model: str, query: str, data: dict) -> dict:
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
        print("[LLM | 0/3] Fetching requirements...", end="\r")
        """
        Note: OpenAI JSON Mode suppressed
            Not used since even with Mono-query returned wrong result for:
                "Check if a cover letter or a motivation letter required.
                If so return True, otherwise False"
        """
        # Requirements
        reqs = {
            "req_lang": "Check if one or more non-English languages are strictly required for this job, replacing ... with this requirement details. If so: '❌ Language required: ...'. Otherwise: '➡️ Language requirement passed'",
            "req_stud": "Check if the candidate is required to be currently enrolled at the university, replacing ... with this requirement details. If required return: '❌ Student status required: ...'. Otherwise: '➡️ Current university student status requirement passed'",
            "req_phd": "Check if a PhD degree is strictly required. If so: '❌ PhD position required'. Otherwise: '➡️ PhD requirement passed'",
            "req_letter": "Check if the cover letter or motivation letter is required, replacing ... with this requirement details. If required return: '✅ Letter required: ...', otherwise '➡️ Letter not required'",
            "req_email": "Check if an email of a recruiter is provided for asking questions regarding the job, replacing ... with the email provided. If provided return: '✅ Email proveded: ...', otherwise '➡️ Email not provided'",
        }
        reqs_out = {}

        debug_str = "[🗣️] LLM - Requirements"
        print(f"{debug_str} - Fetching 5 requirements...", end="\r")

        def fetch_requirement(req_name, req_desc, page_content):
            return req_name, self._openai_query(
                "gpt-4o-2024-11-20", req_desc, page_content
            )

        # Make LLM requests in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    fetch_requirement, req_name, req_desc, page_content
                ): req_name
                for req_name, req_desc in reqs.items()
            }
            for future in concurrent.futures.as_completed(futures):
                req_name, res = future.result()
                reqs_out[req_name] = res

        print(f"{debug_str} - Fetched {len(list(reqs))} requirements      ", end="\r")
        return reqs_out

    def fix_page_descr(self, page_descr: str) -> str:
        debug_str = "[🗣️] LLM"
        print(f"{debug_str} - Page description fix...", end="\r")
        page_descr_fix = self._groq_query(
            "llama-3.3-70b-versatile",
            r"""
            Check if the markdown syntax is correct. If not, fix it.
            Output only the markdown.
            Remove all **bold** and *italic* text, but keep formatting in ***bold italic***.
            Syntax:
                - if there is a list, use '-' instead of '*'.
                - do not use html tags like '<br/>'.
                - never use leading spaces in the beginning of the line.
            """,
            page_descr,
        )
        print(f"{debug_str} - Page description fixed           ")
        return page_descr_fix
