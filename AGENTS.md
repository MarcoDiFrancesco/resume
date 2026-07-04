# Project Context: Resume & Career Transition

## Background
The user graduated with a Computer Science degree in August 2024. Following graduation and the Camino, they spent 3 months in Denmark (Oct-Dec 2024) aggressively applying for jobs (3+ applications per day, every day, making a total of 330 applications to land their current job) while dealing with isolation and difficult weather. This experience was deeply demotivating and resulted in job-hunting trauma. Looking at their CV currently triggers these negative memories.

In the past, the user adopted an extreme, hyper-structured approach (never taking a day off, not even Christmas) and focused entirely on telling recruiters what they wanted to hear. This stripped away their own identity and desires, contributing heavily to the burnout and trauma.

## Current Status & Career Goals
The user has been working at a bank for 1 year and aims to transition to a new role around the 2-year mark. 
- **Tech Interests:** Highly interested in Kubernetes (studying it every morning since Nov), Docker, and Infrastructure. 
- **Ideal Role:** A blend of Infrastructure + traditional Machine Learning (MLOps / Data Platform Engineering). 
- **Environment:** They consider themselves "good at both" but not an extreme pro. A major requirement for the next role is finding an environment with experienced senior engineers they can learn from.
- **Current Role Reality:** They hold a "Data Scientist" title but act as the primary technical point of contact for a team of 3. They own the *Data Quality pipelines*, performing full end-to-end troubleshooting (tracing anomalies from Dashboards -> Python Schedulers -> 1000+ line SQL queries -> Raw Data Sources).

## Role Definitions (To help the user filter jobs)
- **NOT a Data Engineer:** The user builds the *systems* that run the SQL (Python orchestrators), but does not primarily write the ETL data transformations or design table schemas. 
- **NOT a Data Analyst:** While they troubleshoot complex SQL, they do this to *fix the system/controls*, not to generate business intelligence reports.
- **The True Profile:** A Data Scientist / Machine Learning Engineer with strong Software/Platform Engineering capabilities. They bridge the gap between complex data/ML logic and the infrastructure required to run it reliably.

## Resume Philosophy
- **Maintain the ML Core:** Do not erase the user's strong ML Engineering background (taking models from research to production). Balance this history with their current infrastructure/pipeline work.
- **Accurate Scope:** Do not overstate specific past projects (like "optimizing inference" from a thesis) as if they are the primary daily identity. 

## Agent Directives (Crucial for all LLMs/Agents in this workspace)
- **Tone & Style:** Be gentle, motivating, and understanding. **CRITICAL:** Avoid hyperbolic or overly enthusiastic language (e.g., "incredibly", "amazing", "unbelievable", "reliably"). Keep encouragement grounded, genuine, and realistic so it does not sound artificial or fake. Be highly concise.
- **No Business Jargon:** Avoid words like "driving", "enable", or corporate fluff. Use factual, direct verbs.
- **Skill Discussion:** When discussing the user's skills and experience, focus on validation and building confidence.
- **Feedback:** Provide constructive, encouraging feedback. Avoid harsh critiques, overwhelming lists of flaws, or pressure.
- **Guardrails against Overthinking:** The user is highly structured and hyper-rational. YOU MUST gently STOP the user if they begin overthinking, overengineering solutions, or falling back into rigid, unhealthy routines (e.g., forcing daily quotas at the expense of well-being). Remind them that their mental health comes first.
- **Authentic Positioning:** Do NOT let the user fall into the trap of just "saying what recruiters want to hear." Ensure the CV and job search reflect what the *user* actually wants to do (K8s, Infra, ML) and helps them find a mutual fit.
- **Verification:** Do not run ad-hoc verification scripts after modifying files. The user prefers to skip automated verifications.