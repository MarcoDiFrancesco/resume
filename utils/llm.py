from openai import OpenAI
from pydantic import BaseModel
import json


class Llm:
    def __init__(self):
        self.client = OpenAI()

    def _query(self, model: str, instructions: str, prompt: str) -> list:
        """Simple LLM query."""
        response = self.client.chat.completions.create(
            model=model,
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

    def _query_json(
        self, model: str, instructions: str, prompt: str, prop_name: str, prop_desc: str
    ) -> dict:
        """LLM query with output in strict json format."""
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "requirements",
                "schema": {
                    "type": "object",
                    "properties": {
                        prop_name: {
                            "type": "string",
                            "description": prop_desc,
                        },
                    },
                    "required": [prop_name],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
        response = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {"role": "user", "content": prompt},
            ],
            response_format=response_format,
        )
        return json.loads(response.choices[0].message.content)

    def fetch_requirements(self, page_content: str):
        print("[LLM]: Fetching requirements...", end="\r")
        instructions = "Fetch the requirements from the job posting."
        """
        Response format:
            Using response_format as json instead of pydantic class since it's not
            possible to specify the description for each property.

        Mono-query vs Multi-query:
            Mono-query used since Multi-query with 4o, temperature 0, fails to
            understand the requirement univeristy. E.g. marks the following
            as being mandatorily a current student:
                "Students from countries outside the EU require a German residence/work permit."

        Model '4o' vs '4o-mini':
            Using 'gpt-4o' since 'gpt-4o-mini' with temperature 0, only one property,
            does not follow the exact specified output. E.g.:
                "\n✔ Current university student status required"
            instead of
                "❌ Current university student status required"
        """
        reqs = {
            "req_lang": "Check if one or more non-English languages are strictly required for this job. If so: '❌ Language required: <LANGUAGE>'. Otherwise: '➡️ Language requirement passed'",
            "req_stud": "Check if the status of 'current a university student' is strictly required. If so: '❌ Current university student status required'. Otherwise: '➡️ Current university student status requirement passed'",
            "req_phd": "Check if a PhD degree is strictly required. If so: '❌ PhD position required'. Otherwise: '➡️ PhD requirement passed'",
        }
        reqs_output = {}

        for requir_name, requir_desc in reqs.items():
            res = self._query_json(
                "gpt-4o",
                instructions,
                page_content,
                requir_name,
                requir_desc,
            )
            reqs_output[requir_name] = res[requir_name]

        print("[LLM]: Requirements fetched    ")
        return reqs_output
