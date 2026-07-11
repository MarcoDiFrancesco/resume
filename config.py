"""Configuration constants for the resume finetune application."""

# URLs
NOTION_PURPOSE_PAGE_URL = "https://www.notion.so/marcodifrancesco/Finding-My-Purpose-2d0187d9db644cf18cf303c39de09203"

# File paths
RESUME_MAIN_FILE = "resume.tex"
COVER_LETTER_FILE = "coverletter.tex"
EMAIL_DRAFT_FILE = "EMAIL_DRAFT.md"
JOB_DESCRIPTION_FILE = "JOB_DESCRIPTION.md"

RESUME_FILES = [
    "cv/1-summary.tex",
    "cv/2-work.tex",
    "cv/3-education.tex",
    "cv/4-technologies.tex",
    "cv/5-keywords.tex",
    "cv/6-projects.tex",
    # "cv/7-extracurricular.tex",
    "header.tex",
]

# Prompt file paths
PROMPT_SUMMARY = "prompts/1-summary.txt"
PROMPT_TECHNOLOGIES = "prompts/4-technologies.txt"
PROMPT_KEYWORDS = "prompts/5-keywords.txt"
PROMPT_HEADER = "prompts/7-header.txt"

# Aider configuration
AIDER_SCRIPT_PATH = "/home/marco/scripts/aider"
AIDER_MODEL = "gemini/gemini-2.5-pro"

# LLM model names
GEMINI_FLASH_MODEL = "gemini-2.5-flash"
LLAMA_MODEL = "llama-3.3-70b-versatile"

# Notion query configuration
NOTION_PAGE_SIZE = 25
