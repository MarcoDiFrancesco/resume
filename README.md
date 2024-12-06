# Commands

## CV

```
(Prompt 1)
Consider the job description in JOB_DESCRIPTION.md. Update resume.tex to match every point in bold italic (using ***); if it's not in bold italic don't mention it. Ensure the tone remains understated, factual, and free from buzzwords or formal corporate language. Avoid adjectives and superlative language like "strong", "leveraging," "seamless," and "high-quality," in favor of clear and neutral descriptions of skills and experience. Keep the tone modest and straightforward.

Edit the following sections:

- Section "SUMMARY": Pick the best summary that fits the role (e.g., ML Engineer, Data Scientist), uncomment it, and update it with every point which is in bold italic. The length of the summary should be around 100 words.
- Section "Work Experience": update the positions at "ABB" and "Fondazione Bruno Kessler" by changing their description. The changes have to be subtile, keep the work experience description of the same idea and only slightly modify the sentences to underline the technologies. Keep the numbers mentioned.
```

```
(Prompt 2)
In section "Education":
- Prioritize the courses most important. Do not add other courses.

In section "Relevant Technologies":
- Prioritize the technologies that they require.
- Remove the technoliges only if they are extremely unrelevant for this position (e.g. Nginx is unrelevant for a data science position), but never remove the ones in "Always show". Put them in the "Optional" comment.
- If not already present add the technologies which are in italic bold.
- Do not add technologies not in italic bold, instead tell me what are other technologies are not listed and I could add.
```

```
(Prompt 3)
In section "Relevant Projects" comment the projects which are irrelevant. Uncomment the ones are relevant.
- Rank them by relevance for this job posting.
- Keep exactly 3 projects.

Check if the preamble has a suitable title: e.g. Data Scientist, Machine Learning Engineer, or Data Engineer; otherwise change it.
```

## Motivation letter

```
(Prompt 4 - Cover letter)
Consider the job description in JOB_DESCRIPTION.md, the CV in resume.tex, and update coverletter.tex to match the requirements of this new job description of this new company. In each section pick up muliple points brought up from the job description.
- IMPORTANT: The changes have to be subtile, keep the description of the same idea and only slightly modify the sentences.
- Keep the cover letter tone extremely technical.
- Why Company section must contain something that is picked up by the job description. Put something tech oriented, and not about the business side.
```

```
Change the \position to what you think it's the most suitable - e.g. Data Scientist, Machine Learning Engineer, Data Engineer - or whatever fits the best.
```
