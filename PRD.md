# PRD — Resume Finetune

## Overview

Streamlit app that uses AI to tailor the resume to a job posting.

## Problem

Editing a resume for every job posting is slow and repetitive. This tool automates it by pulling postings from Notion, checking requirements, and rewriting resume sections with LLMs based on which parts of the posting the user highlighted as relevant.

## Features

The app follows a linear flow per posting:

1. **Fetch posting** — Pull the next unprocessed posting from Notion. Show title, company, age, and link to source.

2. **Check requirements** — Present the key job requirements in an easy-to-read pass/fail table. This helps the user quickly spot any dealbreakers and decide whether to move forward with the posting. The table covers: required languages, student or PhD status, years of experience, need for a cover letter, and presence of a recruiter email.

3. **Highlight keywords** — The user reviews the posting in Notion and highlights (bold-italic) the parts that match their experience. For example, a technology the user knows but isn't on the base resume gets highlighted and will appear in the rewrite. Anything not highlighted is ignored.

4. **Clean markdown** — Fix the job description formatting (strip bold/italic, fix lists, remove HTML). Skipped if highlights are already present.

5. **Rewrite resume** — Update relevant sections of the resume (such as the summary and technologies) to reflect the highlighted keywords of the job description.

Beyond the per-posting flow, the app also provides DB maintenance tools:

- **Markdown fix** — Clean formatting across the page.
- **Duplicate detection** — Flag postings that match previous applications.
- **Missing CV** — Once applied, flag postings in Notion that have no CV attached.
