from aider.coders import Coder
from aider.models import Model
from utils.utils import check_files_existance
import sys
import os
import time

INSTRUCTIONS = """
Do not ask me "Run shell command?", or any other command.
"""

PROMPT_1 = """
(Prompt Resume 1 - v4)

Consider the job description in JOB_DESCRIPTION.md. Update resume.tex to match every point in bold italic (using ***); if it's not in bold italic don't mention it. 
- Tone: Ensure the tone remains modest, factual, and free from buzzwords and corporate jargon. Avoid adjectives and superlative language like "strong", "leveraging," "seamless," and "high-quality," in favor of clear and neutral descriptions of skills and experience.

Edit the following sections:

- "Summary": Pick the best summary that fits the role (e.g., ML Engineer, Data Scientist), uncomment it, and update it with every point which is in bold italic. The length of the summary should be around 100 words.
- "Work Experience": update the positions at "ABB" and "Fondazione Bruno Kessler" by changing their description. The changes have to be subtile, keep the work experience description of the same idea and only slightly modify the sentences to underline the technologies. Keep the numbers mentioned.
"""


PROMPT_2 = """
(Prompt Resume 2 - v4)

In section "Education":
- Reorder the courses from most important to the least important. Do not change or add courses.

In section "Relevant Technologies":
- Prioritize the technologies that they require.
- Remove the technoliges only if they are extremely unrelevant for this position (e.g. Nginx is unrelevant for a data science position), but never remove the ones in "Always show". Put them in the "Optional" comment.
- If not already present add the technologies which are in italic bold.
- Do not add technologies not in italic bold, instead tell me what are other technologies are not listed and I could add.
"""


PROMPT_3 = """
(Prompt Resume 3 - v4)

In section "Relevant Projects" comment the projects which are irrelevant. Uncomment the ones are relevant.
- Rank them by relevance for this job posting.
- Keep exactly 3 projects.

Check if the preamble has a suitable job title: e.g. Data Scientist, Machine Learning Engineer, or Data Engineer; otherwise change it.
"""


PROMPT_RESUME_ADDRESS = rf"""
(Prompt Resume City - v4)

Check if \address in resume.tex is the one specified in JOB_DESCRIPTION.md under 'My Address'.
If not, update the address in resume.tex to be exactly the one specified in JOB_DESCRIPTION.md.
"""

PROMPT_COVER_LETTER = """
(Prompt Cover Letter - v4)

Consider the job description in JOB_DESCRIPTION.md, the CV in resume.tex, and update coverletter.tex to match the requirements of this new job description of this new company. In each section pick up muliple points brought up from the job description.
- IMPORTANT: The changes have to be subtile, keep the description of the same idea and only slightly modify the sentences.
- Keep the cover letter tone technical. Do not write any corporate jargon. Do not write adjectives like "particularly interested" and instead write only "interested".

Specific sectinons:
- "Why Company" keep the reason that I want to change from a large corporation to a smaller company.
"""

PROMPT_EMAIL_TEMPLATE = """
(Prompt Email Draft - v4)

Rewrite the EMAIL_DRAFT.md to fit the JOB_DESCRIPTION.md. Rewrite the 2 questions to fit the job description. 
- Keep them without corporate jargon and keep the tone very technical.
- Do not write my experience, only make the questions.
"""


class Aider:
    def __init__(self):
        fnames = ["resume.tex", "JOB_DESCRIPTION.md"]
        check_files_existance(fnames)

        model = Model("sonnet")
        self.coder = Coder.create(main_model=model, fnames=fnames, auto_commits=False)

    def _run_prompt(self, prompt):
        """Executes `self.coder.run(prompt)`."""
        self.coder.run(prompt)

    def _run_prompt_silent(self, prompt):
        """Executes `self.coder.run(prompt)` disabling output."""
        original_stdout = sys.stdout
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull
            self.coder.run(prompt)
        sys.stdout = original_stdout

    def run_resume_prompt(self, prompt, file, num, tot):
        print(f"[Aider] - {file} prompt {num}/{tot}. Running...", end="\r")
        start = time.time()
        self._run_prompt_silent(prompt)
        end = time.time()
        print(
            f"[Aider] - {file} prompt {num}/{tot}. Done in {end-start:.0f} sec. Session cost: {self.coder.total_cost:.2f}$"
        )

    def update_resume(self):
        self.run_resume_prompt(INSTRUCTIONS + PROMPT_1, "Resume", 1, 4)
        self.run_resume_prompt(PROMPT_2, "Resume", 2, 4)
        self.run_resume_prompt(PROMPT_3, "Resume", 3, 4)
        self.run_resume_prompt(PROMPT_RESUME_ADDRESS, "Resume", 4, 4)

    def update_cover_letter(self, requirements_files):
        if not requirements_files["req_letter"]:
            while True:
                inpt = input(
                    "[Aider] Cover Letter not required. Update it anyway? [y/n]: "
                )
                if inpt == "y":
                    break
                elif inpt == "n":
                    return

        self.coder.add_rel_fname("coverletter.tex")
        self.run_resume_prompt(INSTRUCTIONS + PROMPT_COVER_LETTER, "Cover Letter", 1, 1)

    def create_email(self, requirements_files):
        if not requirements_files["req_email"]:
            while True:
                inpt = input("[Aider] Email not required. Update it anyway? [y/n]: ")
                if inpt == "y":
                    break
                elif inpt == "n":
                    return

        self.coder.add_rel_fname("EMAIL_DRAFT.md")
        self.run_resume_prompt(INSTRUCTIONS + PROMPT_EMAIL_TEMPLATE, "Email", 1, 1)
