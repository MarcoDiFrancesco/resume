from openai import OpenAI


class Llm:
    def __init__(self):
        self.client = OpenAI()

    def _query(self, instructions: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
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

    def html_to_md(self, desc_html: str) -> str:
        instructions = "Make this html code into markdown. Remove the trailing spaces and slashes. Only print the markdown without a code block."
        return self._query(
            instructions,
            desc_html,
        )
