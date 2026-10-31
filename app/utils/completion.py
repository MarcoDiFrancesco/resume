"""Text completion utilities using OpenAI compatible endpoint."""

from openai import OpenAI

from app.config import GEMINI_FLASH_LITE_MODEL

MARKDOWN_CLEAN_PROMPT = r"""
Check if the markdown syntax is correct. If not, fix it.
Output only the markdown.
Syntax:
    - if there is a list, use '-' instead of '*'.
    - do not use html tags like '<br/>'.
    - do not use leading spaces in the beginning of the line.
    - do not format links in markdown, instead in plain text in square brackets, e.g. [https://linkedin.com/xyz].
    - preserve line breaks as in the original text, including double line breaks (\n\n).
    - Remove all **bold** and *italic* formatting. Then, add in h3 (with hashtags) the section headings, and **bold** the subsections.
"""


def clean_markdown_description(page_descr: str) -> str:
    """Format and clean job description markdown using LLM."""
    client = OpenAI()
    response = client.chat.completions.create(
        model=GEMINI_FLASH_LITE_MODEL,
        messages=[
            {
                "role": "system",
                "content": MARKDOWN_CLEAN_PROMPT,
            },
            {
                "role": "user",
                "content": page_descr,
            },
        ],
    )
    content = response.choices[0].message.content
    assert content, "Error in query generation"
    return content
