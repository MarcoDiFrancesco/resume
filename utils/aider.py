from aider.coders import Coder
from aider.models import Model
from utils.utils import files_exist
import sys
import os
import time

INSTRUCTIONS = rf"""
Intrustions:
- For every change you do the tone must remain modest, factual, and free from buzzwords and corporate jargon. Never use adjectives or superlative words like: 'best', 'complex', 'strong', 'leveraging', 'seamless' etc.
- Do not ask me 'Run shell command?', or any other command.
"""

PROMPT_HEADER_ADDRESS = rf"""
{INSTRUCTIONS}
(Prompt Header - v7)

Make the following changes in header.tex
- Check if \address in is the one specified in JOB_DESCRIPTION.md under 'My Address'. 
    If not, update it to be exactly the one specified in JOB_DESCRIPTION.md.
"""

PROMPT_RESUME_SUMMARY_WORK = rf"""
{INSTRUCTIONS}
(Prompt Resume 1 - v7)

JOB_DESCRIPTION.md highlights skills I have in ***bold italic***. Update resume.tex to reflect only these skills or those already mentioned in the resume. Exclude skills not in bold italic, even if required in the job.

In section 'Summary':
- Update it mentioning my skill and my work experience relevant for this job. Do not mention specific technologies like Docker, Python, etc.
- Keep a length of around 100 words.

In section 'Work Experience':
- Update the job descriptions. The changes have to be subtile, slightly modify the sentences to underline the technologies or skills if relevant.
- Keep the numbers, and technologies mentioned.
"""

PROMPT_RESUME_EDU_TECH = rf"""
(Prompt Resume 2 - v7)

In section 'Education':
- Reorder the courses from most important to the least important. Do not change or add courses.

In section 'Relevant Technologies':
- Write the technologies specified in 'Always show' + choose the most relevant ones between 'Optional' and the ones in ***bold italic*** in the job posting.
- If technologies in the job posting are not in ***bold italic*** do not add them.
- Use between 5 and 8 technologies for each section.
"""


PROMPT_RESUME_PROJ = rf"""
(Prompt Resume 3 - v7)

In section 'Relevant Projects':
- Comment the projects which are irrelevant. Uncomment the ones are relevant.
- Rank them by relevance for this job posting.
- Keep exactly 3 projects.
"""

PROMPT_RESUME_ADD_KEYWORDS = rf"""
(Prompt Resume 4 - v7)

In section 'Additional Keywords':
- Gather all the keywords missing from the resume.tex but present in JOB_DESCRIPTION.md, that would improve the resume score of an ATS keyword scanner.
"""

PROMPT_LETTER = rf"""
{INSTRUCTIONS}
(Prompt Cover Letter - v7)

Update the cover letter (in coverletter.tex) to match the requirements of a new job description (in JOB_DESCRIPTION.md) for the job posting new company, considering the resume (in resume.tex). In each of the 3 sections pick up muliple points brought up from the job description and resume.

Specific to 'Why Company' section:
- Keep the reason that I want to change from a large corporation to a smaller company.
- Replace 'COMPANY-NAME' with the company name from the job description.
"""

PROMPT_EMAIL = rf"""
{INSTRUCTIONS}
(Prompt Email Draft - v7)

Rewrite the EMAIL_DRAFT.md to fit the JOB_DESCRIPTION.md. Rewrite the 2 questions to fit the job description.
- Keep them without corporate jargon and keep the tone very technical.
- Do not write my experience, only make the questions.
"""


class Aider:
    def __init__(self):
        self.model = Model("sonnet")

    def _reset(self):
        self.coder: Coder = Coder.create(main_model=self.model, auto_commits=False)

    def _add_files(self, fnames):
        files_exist(fnames)
        for fname in fnames:
            self.coder.add_rel_fname(fname)

    def _prompt(self, prompt, file, num, tot):
        print(f"[Aider] - {file} prompt {num}/{tot}. Running...", end="\r")
        start = time.time()

        # Execute `self.coder.run(prompt)` disabling output.
        original_stdout = sys.stdout
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull
            self.coder.run(prompt)
        sys.stdout = original_stdout

        end = time.time()
        print(
            f"[Aider] - {file} prompt {num}/{tot}. Done in {end-start:.0f} sec. Session cost: {self.coder.total_cost:.2f}$"
        )

    def update_header(self):
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", "header.tex"])
        self._prompt(PROMPT_HEADER_ADDRESS, "Header", 1, 1)

    def update_resume(self):
        """
        Update resume.tex with Aider to match the job description.
        """
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", "resume.tex"])
        self._prompt(PROMPT_RESUME_SUMMARY_WORK, "Resume", 1, 4)
        self._prompt(PROMPT_RESUME_EDU_TECH, "Resume", 2, 4)
        self._prompt(PROMPT_RESUME_PROJ, "Resume", 3, 4)
        self._prompt(PROMPT_RESUME_ADD_KEYWORDS, "Resume", 4, 4)

    def update_cover_letter(self):
        """
        Update coverletter.tex with Aider.
        """
        while True:
            inpt = input(
                "[Aider] Cover Letter not requested. Update it anyway? [y/n]: "
            )
            if inpt == "y":
                break
            elif inpt == "n":
                return
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", "resume.tex", "coverletter.tex"])
        self._prompt(PROMPT_LETTER, "Cover Letter", 1, 1)

    def update_email(self):
        while True:
            inpt = input("[Aider] Email not provided. Update it anyway? [y/n]: ")
            if inpt == "y":
                break
            elif inpt == "n":
                return
        self._reset()
        self._add_files(["JOB_DESCRIPTION.md", "resume.tex", "EMAIL_DRAFT.md"])
        self._prompt(PROMPT_EMAIL, "Email", 1, 1)
