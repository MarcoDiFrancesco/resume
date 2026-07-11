"""Configuration constants for the resume finetune application."""

# URLs
NOTION_PURPOSE_PAGE_URL = "https://www.notion.so/marcodifrancesco/Finding-My-Purpose-2d0187d9db644cf18cf303c39de09203"

# File paths
RESUME_MAIN_FILE = "latex/resume.tex"
COVER_LETTER_FILE = "latex/coverletter.tex"
EMAIL_DRAFT_FILE = "app/data/EMAIL_DRAFT.md"
JOB_DESCRIPTION_FILE = "app/data/JOB_DESCRIPTION.md"

RESUME_FILES = [
    "latex/cv/1-summary.tex",
    "latex/cv/2-work.tex",
    "latex/cv/3-education.tex",
    "latex/cv/4-technologies.tex",
    "latex/cv/5-keywords.tex",
    "latex/cv/6-projects.tex",
    # "latex/cv/7-extracurricular.tex",
    "latex/header.tex",
]

# Prompt file paths
PROMPT_SUMMARY = "app/prompts/1-summary.txt"
PROMPT_TECHNOLOGIES = "app/prompts/4-technologies.txt"
PROMPT_KEYWORDS = "app/prompts/5-keywords.txt"
PROMPT_HEADER = "app/prompts/7-header.txt"

# Aider configuration
AIDER_SCRIPT_PATH = "/home/marco/scripts/aider"
AIDER_MODEL = "gemini/gemini-2.5-pro"

# LLM model names
GEMINI_FLASH_MODEL = "gemini-2.5-flash"
LLAMA_MODEL = "llama-3.3-70b-versatile"

# Notion query configuration
NOTION_PAGE_SIZE = 25
