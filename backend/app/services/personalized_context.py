from typing import Any, Dict, List, Optional


def _clean_list(value: Any) -> List[str]:
    if not value:
        return []

    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return []


def _clean_dict(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}

    return value


def build_personalized_context(
    resume_profile: Optional[Dict[str, Any]] = None,
    job_profile: Optional[Dict[str, Any]] = None,
    match_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    resume_profile = _clean_dict(resume_profile)
    job_profile = _clean_dict(job_profile)
    match_result = _clean_dict(match_result)

    resume_skills = _clean_list(
        resume_profile.get("skills")
        or resume_profile.get("technical_skills")
    )

    projects = _clean_list(
        resume_profile.get("projects")
    )

    experience = _clean_list(
        resume_profile.get("experience")
    )

    education = _clean_list(
        resume_profile.get("education")
    )

    required_skills = _clean_list(
        job_profile.get("required_skills")
    )

    preferred_skills = _clean_list(
        job_profile.get("preferred_skills")
    )

    responsibilities = _clean_list(
        job_profile.get("responsibilities")
    )

    matched_skills = _clean_list(
        match_result.get("matched_skills")
        or match_result.get("matching_skills")
    )

    missing_skills = _clean_list(
        match_result.get("missing_skills")
        or match_result.get("missing_required_skills")
    )

    additional_context = {
        "candidate": {
            "skills": resume_skills,
            "projects": projects,
            "experience": experience,
            "education": education,
        },

        "target_role": {
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "responsibilities": responsibilities,
        },

        "alignment": {
            "matched_skills": matched_skills,
            "missing_required_skills": missing_skills,
        },

        "raw_resume_profile": resume_profile,
        "raw_job_profile": job_profile,
        "raw_match_result": match_result,
    }

    return additional_context


def format_personalized_context(
    context: Dict[str, Any]
) -> str:

    candidate = context.get(
        "candidate",
        {}
    )

    target_role = context.get(
        "target_role",
        {}
    )

    alignment = context.get(
        "alignment",
        {}
    )

    sections = []

    skills = candidate.get("skills", [])
    if skills:
        sections.append(
            "Candidate Skills:\n"
            + "\n".join(f"- {skill}" for skill in skills)
        )

    projects = candidate.get("projects", [])
    if projects:
        sections.append(
            "Candidate Projects:\n"
            + "\n".join(f"- {project}" for project in projects)
        )

    experience = candidate.get("experience", [])
    if experience:
        sections.append(
            "Candidate Experience:\n"
            + "\n".join(f"- {item}" for item in experience)
        )

    education = candidate.get("education", [])
    if education:
        sections.append(
            "Candidate Education:\n"
            + "\n".join(f"- {item}" for item in education)
        )

    required_skills = target_role.get(
        "required_skills",
        []
    )

    if required_skills:
        sections.append(
            "Required Job Skills:\n"
            + "\n".join(
                f"- {skill}"
                for skill in required_skills
            )
        )

    preferred_skills = target_role.get(
        "preferred_skills",
        []
    )

    if preferred_skills:
        sections.append(
            "Preferred Job Skills:\n"
            + "\n".join(
                f"- {skill}"
                for skill in preferred_skills
            )
        )

    responsibilities = target_role.get(
        "responsibilities",
        []
    )

    if responsibilities:
        sections.append(
            "Job Responsibilities:\n"
            + "\n".join(
                f"- {item}"
                for item in responsibilities
            )
        )

    matched_skills = alignment.get(
        "matched_skills",
        []
    )

    if matched_skills:
        sections.append(
            "Matched Skills:\n"
            + "\n".join(
                f"- {skill}"
                for skill in matched_skills
            )
        )

    missing_skills = alignment.get(
        "missing_required_skills",
        []
    )

    if missing_skills:
        sections.append(
            "Missing Required Skills:\n"
            + "\n".join(
                f"- {skill}"
                for skill in missing_skills
            )
        )

    return "\n\n".join(sections)