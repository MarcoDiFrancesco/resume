from aider.coders import Coder
from aider.models import Model
from utils.utils import check_files_existance


PROMPT_1 = """
To not ask me "Run shell command?"

(Prompt 1)
Consider the job description in JOB_DESCRIPTION.md. Update resume.tex to match every point in bold italic (using ***); if it's not in bold italic don't mention it. Ensure the tone remains understated, factual, and free from buzzwords or formal corporate language. Avoid adjectives and superlative language like "strong", "leveraging," "seamless," and "high-quality," in favor of clear and neutral descriptions of skills and experience. Keep the tone modest and straightforward.

Edit the following sections:

- Section "SUMMARY": Pick the best summary that fits the role (e.g., ML Engineer, Data Scientist), uncomment it, and update it with every point which is in bold italic. The length of the summary should be around 100 words.
- Section "Work Experience": update the positions at "ABB" and "Fondazione Bruno Kessler" by changing their description. The changes have to be subtile, keep the work experience description of the same idea and only slightly modify the sentences to underline the technologies. Keep the numbers mentioned.
"""


PROMPT_2 = """
(Prompt 2)
In section "Education":
- Reorder the courses from most important to the least important. Do not change or add courses.

In section "Relevant Technologies":
- Prioritize the technologies that they require.
- Remove the technoliges only if they are extremely unrelevant for this position (e.g. Nginx is unrelevant for a data science position), but never remove the ones in "Always show". Put them in the "Optional" comment.
- If not already present add the technologies which are in italic bold.
- Do not add technologies not in italic bold, instead tell me what are other technologies are not listed and I could add.
"""


PROMPT_3 = """
(Prompt 3)
In section "Relevant Projects" comment the projects which are irrelevant. Uncomment the ones are relevant.
- Rank them by relevance for this job posting.
- Keep exactly 3 projects.

Check if the preamble has a suitable title: e.g. Data Scientist, Machine Learning Engineer, or Data Engineer; otherwise change it.
Choose the address closer to the job location.
"""

PROMPT_EMAIL_TEMPLATE = """
(Prompt: Email Draft)
Consider the two cases depending if there is a recruiter email in JOB_DESCRIPTION.md:
- If there is an email: rewrite the EMAIL_DRAFT.md to fit the JOB_DESCRIPTION.md. Do not write my experience, only make the questions.
- If there is no email: refuse to answer with only "❌ No email provided in the job description.".
"""


class Aider:
    def __init__(self):
        fnames = ["resume.tex", "JOB_DESCRIPTION.md"]
        # Check if fnames files exists
        check_files_existance(fnames)

        model = Model("sonnet")
        self.coder = Coder.create(main_model=model, fnames=fnames, auto_commits=False)

    def run_prompts(self):
        self.coder.run(PROMPT_1)
        self.coder.run(PROMPT_2)
        self.coder.run(PROMPT_3)

        self.coder.add_rel_fname("EMAIL_DRAFT.md")
        self.coder.run(PROMPT_EMAIL_TEMPLATE)
