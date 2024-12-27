from openai import OpenAI
from pydantic import BaseModel


class Llm:
    def __init__(self):
        self.client = OpenAI()

    def _query(self, instructions: str, prompt: str) -> str:
        """Simple LLM query."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {"role": "user", "content": prompt},
            ],
        )
        resp = response.choices[0].message.content
        resp_list = resp.split("\n")
        return resp_list

    def _query_json(self, instructions: str, prompt: str, response_format) -> dict:
        """LLM query with strict json format."""
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {"role": "user", "content": prompt},
            ],
            response_format=response_format,
        )
        output = completion.choices[0].message.parsed
        from pdb import set_trace; set_trace()
        return output

    def fetch_requirements(self, page_content: str):
        print("[LLM]: Fetching requirements...", end="\r")

        instructions = """
        Fetch the requirements:

        ## req_lang:
        Check if one or more non-English languages are strictly required.
        - If so: '❌ Language required: <LANGUAGE>'
        - Otherwise: '➡️ Language requirement passed'

        ## req_stud
        Check if the candidate must be a current university student.
        - If so: '❌ Current university student status required'
        - Otherwise: '➡️ Current university student status requirement passed'

        ## req_phd
        Check if a PhD is strictly required.
        - If PhD position is required: '❌ PhD position required'
        - Otherwise: '➡️ PhD requirement passed'
        """

        class Requirements(BaseModel):
            req_lang: str
            req_stud: str
            req_phd: str

        res = self._query_json(
            instructions,
            page_content,
            Requirements,
        )
        print("[LLM]: Requirements fetched    ")
        return res
