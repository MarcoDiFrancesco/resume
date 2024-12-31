from openai import OpenAI
from pydantic import BaseModel
import json


class Llm:
    def __init__(self):
        self.client = OpenAI()

    def _query(self, model: str, instructions: str, prompt: str) -> list:
        """Simple LLM query.
                
        Prompt caching:
            Enabled automatically at 1024 tokens. Average job posting is 300-800.
            Get cached tokens with:
            `response.usage.prompt_tokens_details.cached_tokens`
        """
        response = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        resp = response.choices[0].message.content
        return resp
        # resp_list = resp.split("\n")
        # return resp_list

    def _query_json(
        self, model: str, instructions: str, prompt: str, prop_name: str, prop_desc: str
    ) -> dict:
        """LLM query with output in strict json format.
        
        Response format:
            Using response_format as json instead of pydantic class since it was not
            possible to specify the description for each property.
        """
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
        print("[LLM | 0/3] Fetching requirements...", end="\r")
        """
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
            "req_stud": "Check if this posting is looking for currently enrolled university. If so: '❌ Current university student status required'. Otherwise: '➡️ Current university student status requirement passed'",
            "req_phd": "Check if a PhD degree is strictly required. If so: '❌ PhD position required'. Otherwise: '➡️ PhD requirement passed'",
        }
        reqs_output = {}

        for idx, (requir_name, requir_desc) in enumerate(reqs.items()):
            print(f"[LLM | {idx+1}/3]: Fetching requirements...", end="\r")
            res = self._query(
                "gpt-4o",
                requir_desc,
                page_content,
            )
            reqs_output[requir_name] = res
        print("[LLM] Requirements fetched           ")
        return reqs_output
