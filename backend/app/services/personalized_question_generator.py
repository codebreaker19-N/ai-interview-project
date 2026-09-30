import json
import re

from app.services.llm import generate_with_ollama


def clean_json_response(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = re.sub(r"```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No valid JSON object found")

    return json.loads(text[start:end + 1])


def build_question_prompt(
    source_value,
    source_type,
    resume_profile,
    job_profile,
    match_result,
    previous_question=None,
    previous_score=None,
    missing_concepts=None
):
    missing_concepts = missing_concepts or []

    return f"""
You are an expert technical interviewer.

Generate ONE personalized technical interview question.

Candidate resume:
{json.dumps(resume_profile, default=str)}

Target job description:
{json.dumps(job_profile, default=str)}

Resume-JD matching:
{json.dumps(match_result, default=str)}

Current focus:
{source_type}: {source_value}

Previous question:
{previous_question}

Previous score:
{previous_score}

Missing concepts from previous answer:
{json.dumps(missing_concepts)}

Rules:

1. The question must be relevant to the candidate and target role.
2. If missing concepts exist, use them to create a useful follow-up.
3. Do not simply repeat the previous question.
4. The question must be answerable in a technical interview.
5. Difficulty should normally be Medium.
6. Provide a technically accurate ideal answer.
7. Provide short IMPORTANT concepts expected in a strong answer.
8. expected_concepts must contain short concept names or phrases.
9. Do NOT write complete sentences inside expected_concepts.
10. Do not require exact wording from the candidate.

Return ONLY valid JSON:

{{
    "question": "Interview question",
    "ideal_answer": "Technically accurate interview answer",
    "expected_concepts": [
        "concept 1",
        "concept 2",
        "concept 3"
    ]
}}
"""


def fallback_question(source_value: str):
    return (
        f"How would you use {source_value} in a practical "
        f"machine learning or data-processing problem?"
    )


def fallback_ideal_answer(source_value: str):
    return (
        f"{source_value} can be used as part of a practical "
        f"machine learning or data-processing workflow. "
        f"The appropriate approach depends on the problem, "
        f"data characteristics, and evaluation requirements."
    )


def fallback_expected_concepts(source_value: str):
    return [
        source_value.lower(),
        "practical application",
        "problem requirements",
        "evaluation"
    ]


def generate_question_and_answer(
    source_value,
    source_type,
    resume_profile,
    job_profile,
    match_result,
    previous_question=None,
    previous_score=None,
    missing_concepts=None
):
    prompt = build_question_prompt(
        source_value=source_value,
        source_type=source_type,
        resume_profile=resume_profile,
        job_profile=job_profile,
        match_result=match_result,
        previous_question=previous_question,
        previous_score=previous_score,
        missing_concepts=missing_concepts
    )

    try:
        response = generate_with_ollama(prompt)

        data = clean_json_response(response)

        question = data.get("question")
        ideal_answer = data.get("ideal_answer")
        expected_concepts = data.get("expected_concepts")

        if not question or not ideal_answer:
            raise ValueError(
                "Question or ideal answer missing"
            )

        if not isinstance(expected_concepts, list):
            expected_concepts = []

        expected_concepts = [
            str(concept).strip()
            for concept in expected_concepts
            if str(concept).strip()
        ]

        if not expected_concepts:
            expected_concepts = fallback_expected_concepts(
                source_value
            )

        return {
            "question": question,
            "ideal_answer": ideal_answer,
            "expected_concepts": expected_concepts
        }

    except Exception:
        return {
            "question": fallback_question(source_value),
            "ideal_answer": fallback_ideal_answer(source_value),
            "expected_concepts": fallback_expected_concepts(
                source_value
            )
        }


def build_source_pool(
    resume_profile,
    job_profile,
    match_result
):
    source_pool = []

    required_missing = (
        match_result.get(
            "missing_required_skills",
            []
        )
    )

    preferred_missing = (
        match_result.get(
            "missing_preferred_skills",
            []
        )
    )

    for skill in required_missing:
        source_pool.append({
            "source_value": skill,
            "category": "gap_required_skill",
            "reason": (
                "Required job skill not strongly "
                "matched in the resume."
            )
        })

    for skill in preferred_missing:
        source_pool.append({
            "source_value": skill,
            "category": "gap_preferred_skill",
            "reason": (
                "Preferred job skill not strongly "
                "matched in the resume."
            )
        })

    for responsibility in (
        job_profile.get("responsibilities", [])
    ):
        source_pool.append({
            "source_value": responsibility,
            "category": "jd_responsibility",
            "reason": (
                "Important responsibility from "
                "the target job."
            )
        })

    for skill in resume_profile.get(
        "skills",
        []
    ):
        source_pool.append({
            "source_value": skill,
            "category": "resume_skill",
            "reason": (
                "Skill explicitly present "
                "in the candidate's resume."
            )
        })

    for project in resume_profile.get(
        "projects",
        []
    ):
        source_pool.append({
            "source_value": project,
            "category": "resume_project",
            "reason": (
                "Project experience from "
                "the candidate's resume."
            )
        })

    return source_pool


def generate_personalized_questions(
    resume_profile,
    job_profile,
    match_result,
    number_of_questions=5
):
    source_pool = build_source_pool(
        resume_profile,
        job_profile,
        match_result
    )

    if not source_pool:
        source_pool = [{
            "source_value": "Machine Learning",
            "category": "general_ml",
            "reason": (
                "General machine learning "
                "interview question."
            )
        }]

    selected_sources = source_pool[
        :number_of_questions
    ]

    questions = []

    previous_question = None
    previous_score = None
    missing_concepts = []

    for source in selected_sources:

        generated = generate_question_and_answer(
            source_value=source["source_value"],
            source_type=source["category"],
            resume_profile=resume_profile,
            job_profile=job_profile,
            match_result=match_result,
            previous_question=previous_question,
            previous_score=previous_score,
            missing_concepts=missing_concepts
        )

        questions.append({
            "question": generated["question"],
            "ideal_answer": generated["ideal_answer"],
            "expected_concepts": generated[
                "expected_concepts"
            ],
            "category": source["category"],
            "topic": source["source_value"],
            "difficulty": "Medium",
            "reason": source["reason"]
        })

        previous_question = generated["question"]

    return {
        "questions": questions
    }