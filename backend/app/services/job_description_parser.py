import json
import re

from ollama import Client

from app.services.llm import OLLAMA_MODEL, OLLAMA_BASE_URL


def clean_json_response(response: str):
    response = response.strip()

    if response.startswith("```"):
        response = re.sub(
            r"^```(?:json)?\s*",
            "",
            response
        )
        response = re.sub(
            r"\s*```$",
            "",
            response
        )

    return response.strip()


def extract_job_profile(text: str):
    client = Client(host=OLLAMA_BASE_URL)

    prompt = f"""
You are an expert job description parser.

Extract ONLY information that is explicitly present
in the job description.

Do not invent, assume, or add information.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "required_skills": [],
    "preferred_skills": [],
    "responsibilities": [],
    "qualifications": []
}}

Rules:

1. required_skills:
   Include technical skills, programming languages,
   frameworks, libraries, databases, AI/ML technologies,
   tools, platforms, and technologies explicitly required.

2. preferred_skills:
   Include skills or technologies explicitly described
   as preferred, nice-to-have, bonus, or desirable.

3. responsibilities:
   Include the actual responsibilities and duties
   mentioned in the job description.

4. qualifications:
   Include explicitly mentioned educational requirements,
   degree requirements, experience requirements,
   certifications, or other eligibility requirements.

5. Do not put responsibilities into required_skills.

6. Do not put qualifications into responsibilities.

7. Do not invent skills from context.

8. If a category is not present, return [].

9. Preserve important technical terminology.

Job Description:

{text}
"""

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]

    content = clean_json_response(content)

    try:
        profile = json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Ollama returned invalid JSON while parsing job description"
        )

    return profile


def parse_job_description(text: str):
    text = text.strip()

    if not text:
        raise RuntimeError(
            "Job description is empty"
        )

    profile = extract_job_profile(text)

    return {
        "text": text,
        "profile": profile
    }