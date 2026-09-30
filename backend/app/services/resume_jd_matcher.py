from app.services.semantic_matching import semantic_skill_match


SKILL_ALIASES = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "machinelearning": "machine learning",

    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit_learn": "scikit-learn",

    "nlp": "natural language processing",
    "natural-language-processing": "natural language processing",

    "cv": "computer vision",
    "computer-vision": "computer vision",

    "dl": "deep learning",
    "deep-learning": "deep learning",

    "genai": "generative ai",
    "gen-ai": "generative ai",
    "generative-ai": "generative ai",

    "tf": "tensorflow",

    "np": "numpy",
    "pd": "pandas",

    "postgres": "postgresql",
    "postgres sql": "postgresql"
}


def normalize_skill(skill: str):
    skill = skill.strip().lower()

    skill = skill.replace("_", " ")
    skill = skill.replace("/", " ")

    skill = " ".join(skill.split())

    return SKILL_ALIASES.get(skill, skill)


def match_skills(
    resume_skills,
    required_skills,
    preferred_skills
):
    resume_map = {
        normalize_skill(skill): skill
        for skill in resume_skills
    }

    required_matched = []
    required_missing = []

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized in resume_map:
            required_matched.append(skill)
        else:
            required_missing.append(skill)

    preferred_matched = []
    preferred_missing = []

    for skill in preferred_skills:
        normalized = normalize_skill(skill)

        if normalized in resume_map:
            preferred_matched.append(skill)
        else:
            preferred_missing.append(skill)

    return {
        "required_matched": required_matched,
        "required_missing": required_missing,
        "preferred_matched": preferred_matched,
        "preferred_missing": preferred_missing
    }


def match_resume_with_job(
    resume_profile: dict,
    job_profile: dict
):
    resume_skills = resume_profile.get("skills", [])

    required_skills = job_profile.get(
        "required_skills",
        []
    )

    preferred_skills = job_profile.get(
        "preferred_skills",
        []
    )

    # -----------------------------
    # STEP 1: Exact + Alias Matching
    # -----------------------------

    exact_matches = match_skills(
        resume_skills,
        required_skills,
        preferred_skills
    )

    exact_required = exact_matches[
        "required_matched"
    ]

    exact_preferred = exact_matches[
        "preferred_matched"
    ]

    exact_required_missing = exact_matches[
        "required_missing"
    ]

    exact_preferred_missing = exact_matches[
        "preferred_missing"
    ]

    # -----------------------------
    # STEP 2: Semantic Matching
    # -----------------------------

    semantic_required, semantic_required_missing = (
        semantic_skill_match(
            resume_skills,
            exact_required_missing
        )
    )

    semantic_preferred, semantic_preferred_missing = (
        semantic_skill_match(
            resume_skills,
            exact_preferred_missing
        )
    )

    # -----------------------------
    # STEP 3: Combine Exact Matches
    # -----------------------------

    final_required_matched = [
        {
            "skill": skill,
            "matched_with": skill,
            "similarity": 100
        }
        for skill in exact_required
    ]

    final_required_matched.extend(
        semantic_required
    )

    final_preferred_matched = [
        {
            "skill": skill,
            "matched_with": skill,
            "similarity": 100
        }
        for skill in exact_preferred
    ]

    final_preferred_matched.extend(
        semantic_preferred
    )

    # -----------------------------
    # STEP 4: Calculate Scores
    # -----------------------------

    required_total = (
        len(final_required_matched)
        + len(semantic_required_missing)
    )

    preferred_total = (
        len(final_preferred_matched)
        + len(semantic_preferred_missing)
    )

    required_score = (
        len(final_required_matched)
        / required_total
        * 100
        if required_total
        else 0
    )

    preferred_score = (
        len(final_preferred_matched)
        / preferred_total
        * 100
        if preferred_total
        else 0
    )

    overall_score = (
        required_score * 0.8
        + preferred_score * 0.2
    )

    return {
        "required_matched": final_required_matched,
        "required_missing": semantic_required_missing,

        "preferred_matched": final_preferred_matched,
        "preferred_missing": semantic_preferred_missing,

        "required_skill_match": round(
            required_score,
            2
        ),

        "preferred_skill_match": round(
            preferred_score,
            2
        ),

        "overall_match": round(
            overall_score,
            2
        )
    }