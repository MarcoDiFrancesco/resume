"""Decisions API integration for evaluating job posting requirements."""

import streamlit as st
from openai import OpenAI

from app.config import DECISION_MODEL

DECISION_QUESTIONS = [
    {
        "name": "req_lang",
        "instructions": "Are any languages other than English or Italian strictly required (e.g., German, French)?",
        "type": "predicate",
    },
    {
        "name": "req_student",
        "instructions": "Is the candidate required to be currently enrolled as a university student or PhD student?",
        "type": "predicate",
    },
    {
        "name": "req_phd",
        "instructions": "Is a PhD degree strictly required?",
        "type": "predicate",
    },
    {
        "name": "req_years",
        "instructions": "Are 5 or more years of professional experience required?",
        "type": "predicate",
    },
    {
        "name": "has_ml",
        "instructions": "Does this role involve working with statistical, machine learning, or AI models?",
        "type": "predicate",
    },
    {
        "name": "has_k8s",
        "instructions": "Does this job description mention explicitly kubernetes?",
        "type": "predicate",
    },
    {
        "name": "req_letter",
        "instructions": "Is a cover letter or motivation letter explicitly required?",
        "type": "predicate",
    },
    {
        "name": "has_email",
        "instructions": "Is a contact email address provided for inquiries?",
        "type": "predicate",
    },
    {
        "name": "has_phone",
        "instructions": "Is a contact phone number provided for inquiries?",
        "type": "predicate",
    },
]

STATUS_MAPPINGS = {
    "req_lang": {
        True: "❌ Non-English/Italian language required",
        False: "➡️ Language requirement passed",
    },
    "req_student": {
        True: "❌ Student / PhD status required",
        False: "➡️ Student / PhD status passed",
    },
    "req_phd": {
        True: "❌ PhD degree required",
        False: "➡️ PhD degree requirement passed",
    },
    "req_years": {
        True: "❌ 5+ years experience required",
        False: "➡️ 5+ experience requirement passed",
    },
    "has_ml": {
        True: "➡️ ML/AI included",
        False: "❌ No ML/AI mentioned",
    },
    "has_k8s": {
        True: "➡️ Kubernetes included",
        False: "❌ No Kubernetes mentioned",
    },
    "req_letter": {
        True: "✅ Letter required",
        False: "➡️ Letter not required",
    },
    "has_email": {
        True: "✅ Email provided",
        False: "➡️ Email not provided",
    },
    "has_phone": {
        True: "✅ Phone provided",
        False: "➡️ Phone not provided",
    },
}


def check_posting_requirements(page_content: str) -> dict[str, bool]:
    """Single call to Decisions API to evaluate posting fit."""
    decision = OpenAI().decisions.create(
        model=DECISION_MODEL,
        input=page_content,
        questions=DECISION_QUESTIONS,
    )
    return {ans.name: ans.probability >= 0.5 for ans in decision.answers}


def display_posting_requirements(page_content: str) -> None:
    """Fetch requirements and display the pass/fail analysis in Streamlit."""
    reqs = check_posting_requirements(page_content)

    st.subheader("📋 Posting Analysis")
    col1, col2 = st.columns([3, 2])

    with col1:
        st.dataframe(
            [
                {
                    "Category": "Language",
                    "Status": STATUS_MAPPINGS["req_lang"][reqs["req_lang"]],
                },
                {
                    "Category": "Student",
                    "Status": STATUS_MAPPINGS["req_student"][reqs["req_student"]],
                },
                {
                    "Category": "PhD",
                    "Status": STATUS_MAPPINGS["req_phd"][reqs["req_phd"]],
                },
                {
                    "Category": "Years",
                    "Status": STATUS_MAPPINGS["req_years"][reqs["req_years"]],
                },
                {
                    "Category": "ML",
                    "Status": STATUS_MAPPINGS["has_ml"][reqs["has_ml"]],
                },
                {
                    "Category": "K8s",
                    "Status": STATUS_MAPPINGS["has_k8s"][reqs["has_k8s"]],
                },
            ],
            column_config={
                "Category": st.column_config.TextColumn(None),
                "Status": st.column_config.TextColumn(None),
            },
            hide_index=True,
            use_container_width=True,
        )

    with col2:
        st.dataframe(
            [
                {
                    "Category": "Letter",
                    "Status": STATUS_MAPPINGS["req_letter"][reqs["req_letter"]],
                },
                {
                    "Category": "Email",
                    "Status": STATUS_MAPPINGS["has_email"][reqs["has_email"]],
                },
                {
                    "Category": "Phone",
                    "Status": STATUS_MAPPINGS["has_phone"][reqs["has_phone"]],
                },
            ],
            column_config={
                "Category": st.column_config.TextColumn(None),
                "Status": st.column_config.TextColumn(None),
            },
            hide_index=True,
            use_container_width=True,
        )
