import re


VALID_CATEGORIES = {
    "resume",
    "project",
    "jd",
    "gap"
}


VALID_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard"
}


VALID_SOURCE_TYPES = {
    "resume_skill",
    "resume_project",
    "resume_item",
    "jd_required_skill",
    "jd_preferred_skill",
    "jd_responsibility",
    "gap_required_skill"
}


SOFT_SKILLS = {
    "communication",
    "teamwork",
    "problem solving",
    "problem-solving",
    "analytical skills",
    "analytical thinking",
    "leadership",
    "time management",
    "strong problem-solving skills",
    "strong problem solving skills"
}


TOPIC_ALIASES = {
    "scikit-learn": {
        "scikit-learn",
        "scikit learn",
        "sklearn"
    },

    "git/github": {
        "git",
        "github",
        "git/github",
        "git / github",
        "experience with git/github"
    },

    "natural language processing": {
        "natural language processing",
        "nlp"
    },

    "generative ai": {
        "generative ai",
        "gen ai",
        "genai"
    },

    "machine learning": {
        "machine learning",
        "ml"
    },

    "deep learning": {
        "deep learning",
        "dl"
    },

    "exploratory data analysis": {
        "exploratory data analysis",
        "eda"
    }
}


EXPERIENCE_PATTERNS = [
    r"\byour experience\b",
    r"\bexperience with\b",
    r"\bexperience in\b",
    r"\bhow have you used\b",
    r"\bhow did you use\b",
    r"\bhow have you applied\b",
    r"\bhow did you apply\b",
    r"\bhow did you implement\b",
    r"\bhow have you implemented\b",
    r"\bwhat have you used\b",
    r"\bwhat did you use\b",
    r"\bwhat libraries have you used\b",
    r"\bwhat technologies have you used\b",
    r"\bwhat algorithms have you used\b",
    r"\bwhat algorithms have you experimented with\b",
    r"\bwhat projects have you built\b",
    r"\bwhat was your role\b",
    r"\bwhat is your role\b",
    r"\bwhat did you contribute\b",
    r"\bhow did you contribute\b",
    r"\bhow have you contributed\b",
    r"\bproject you worked on\b",
    r"\bprojects you worked on\b",
    r"\bproject you worked with\b",
    r"\bprojects you worked with\b",
    r"\bexample of a project\b",
    r"\bexample of a project you\b",
    r"\bworked on a project\b",
    r"\bworked on projects\b",
    r"\bused in your projects\b",
    r"\bapplied in your projects\b",
    r"\bcontributed to a project\b",
    r"\bcontributed to projects\b",
    r"\bprojects you participated in\b"
]


GENERIC_PATTERNS = [
    r"\bhow do you stay up[- ]to[- ]date\b",
    r"\bhow do you stay updated\b",
    r"\bwhat are your strengths\b",
    r"\bwhat are your weaknesses\b",
    r"\bwhy should we hire you\b",
    r"\btell me about yourself\b",
    r"\bwhat are your career goals\b",
    r"\bwhere do you see yourself\b"
]


def normalize(text: str):
    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


def canonical_topic(topic: str):

    normalized = normalize(topic)

    for canonical, aliases in TOPIC_ALIASES.items():

        normalized_aliases = {
            normalize(alias)
            for alias in aliases
        }

        if normalized in normalized_aliases:
            return normalize(canonical)

    return normalized


def topics_match(
    topic1: str,
    topic2: str
):

    if not topic1 or not topic2:
        return False

    return (
        canonical_topic(topic1)
        == canonical_topic(topic2)
    )


def is_soft_skill(topic: str):

    normalized = normalize(topic)

    return normalized in {
        normalize(skill)
        for skill in SOFT_SKILLS
    }


def contains_experience_claim(question: str):

    normalized = normalize(question)

    for pattern in EXPERIENCE_PATTERNS:

        if re.search(
            pattern,
            normalized
        ):
            return True

    return False

def contains_multiple_topics(
    question: str,
    topic: str
):
    """
    Reject questions that clearly combine multiple
    technical subjects.
    """

    normalized_question = normalize(question)
    normalized_topic = normalize(topic)

    topic_words = set(
        normalized_topic.split()
    )

    technical_topics = [
        "python",
        "machine learning",
        "scikit-learn",
        "sql",
        "pandas",
        "numpy",
        "tensorflow",
        "pytorch",
        "generative ai",
        "natural language processing",
        "git",
        "github",
        "data structures",
        "statistics",
        "data analysis",
        "exploratory data analysis",
        "nosql",
        "deep learning",
        "computer vision"
    ]

    detected = []

    for candidate in technical_topics:

        if normalize(candidate) == normalized_topic:
            continue

        pattern = r"\b" + re.escape(
            normalize(candidate)
        ) + r"\b"

        if re.search(
            pattern,
            normalized_question
        ):
            detected.append(candidate)

    # Ignore topic words themselves.
    if detected:
        return True

    # Explicit multi-topic connectors.
    multi_topic_patterns = [
        r"\band\b",
        r"\bor\b",
        r"\bvs\b",
        r"\bversus\b",
        r"\bcompared with\b",
        r"\bcompared to\b",
        r"\bdifference between\b"
    ]

    # Only treat these as a problem when
    # another technical topic was detected.
    for pattern in multi_topic_patterns:

        if re.search(
            pattern,
            normalized_question
        ) and detected:
            return True

    return False


def contains_generic_question(question: str):

    normalized = normalize(question)

    for pattern in GENERIC_PATTERNS:

        if re.search(
            pattern,
            normalized
        ):
            return True

    return False


def get_resume_skills(resume_profile: dict):

    skills = resume_profile.get(
        "skills",
        []
    )

    if not isinstance(skills, list):
        return []

    return [
        skill.strip()
        for skill in skills
        if isinstance(skill, str)
        and skill.strip()
    ]


def get_resume_projects(resume_profile: dict):

    projects = resume_profile.get(
        "projects",
        []
    )

    if not isinstance(projects, list):
        return []

    return [
        project.strip()
        for project in projects
        if isinstance(project, str)
        and project.strip()
    ]


def get_resume_items(resume_profile: dict):

    fields = [
        "skills",
        "projects",
        "experience",
        "education",
        "achievements",
        "leadership",
        "certifications"
    ]

    items = []

    for field in fields:

        values = resume_profile.get(
            field,
            []
        )

        if not isinstance(values, list):
            continue

        for value in values:

            if isinstance(value, str):
                value = value.strip()

                if value:
                    items.append(value)

    return items


def get_required_skills(job_profile: dict):

    values = job_profile.get(
        "required_skills",
        []
    )

    if not isinstance(values, list):
        return []

    return [
        value.strip()
        for value in values
        if isinstance(value, str)
        and value.strip()
    ]


def get_preferred_skills(job_profile: dict):

    values = job_profile.get(
        "preferred_skills",
        []
    )

    if not isinstance(values, list):
        return []

    return [
        value.strip()
        for value in values
        if isinstance(value, str)
        and value.strip()
    ]


def get_responsibilities(job_profile: dict):

    values = job_profile.get(
        "responsibilities",
        []
    )

    if not isinstance(values, list):
        return []

    return [
        value.strip()
        for value in values
        if isinstance(value, str)
        and value.strip()
    ]


def exact_or_alias_in_list(
    topic: str,
    values: list
):

    for value in values:

        if topics_match(
            topic,
            value
        ):
            return True

    return False


def skill_exists_in_resume(
    topic: str,
    resume_profile: dict
):

    return exact_or_alias_in_list(
        topic,
        get_resume_skills(resume_profile)
    )


def project_exists_in_resume(
    topic: str,
    resume_profile: dict
):

    normalized_topic = normalize(topic)

    for project in get_resume_projects(
        resume_profile
    ):

        if normalize(project) == normalized_topic:
            return True

    return False


def required_skill_exists_in_jd(
    topic: str,
    job_profile: dict
):

    return exact_or_alias_in_list(
        topic,
        get_required_skills(job_profile)
    )


def preferred_skill_exists_in_jd(
    topic: str,
    job_profile: dict
):

    return exact_or_alias_in_list(
        topic,
        get_preferred_skills(job_profile)
    )


def responsibility_exists_in_jd(
    source_value: str,
    job_profile: dict
):

    normalized_source = normalize(
        source_value
    )

    responsibilities = get_responsibilities(
        job_profile
    )

    for responsibility in responsibilities:

        normalized_responsibility = normalize(
            responsibility
        )

        if (
            normalized_source
            == normalized_responsibility
        ):
            return True

    return False


def source_is_valid(
    question: dict,
    resume_profile: dict,
    job_profile: dict
):
    if is_soft_skill(source_value):
     return False

    source_type = question.get(
        "source_type"
    )

    source_value = question.get(
        "source_value"
    )

    topic = question.get(
        "topic"
    )

    if not isinstance(
        source_type,
        str
    ):
        return False

    if not isinstance(
        source_value,
        str
    ):
        return False

    if not isinstance(
        topic,
        str
    ):
        return False

    source_type = source_type.strip()
    source_value = source_value.strip()
    topic = topic.strip()

    if source_type not in VALID_SOURCE_TYPES:
        return False

    if not source_value:
        return False

    if not topic:
        return False

    # Topic MUST correspond to the source value.
    if not topics_match(
        topic,
        source_value
    ):
        return False

    # ---------------------------------------------
    # Resume skill
    # ---------------------------------------------

    if source_type == "resume_skill":

        return skill_exists_in_resume(
            source_value,
            resume_profile
        )

    # ---------------------------------------------
    # Resume project
    # ---------------------------------------------

    if source_type == "resume_project":

        return project_exists_in_resume(
            source_value,
            resume_profile
        )

    # ---------------------------------------------
    # Resume generic item
    # ---------------------------------------------

    if source_type == "resume_item":

        normalized_source = normalize(
            source_value
        )

        return any(
            normalize(item)
            == normalized_source
            for item in get_resume_items(
                resume_profile
            )
        )

    # ---------------------------------------------
    # JD required skill
    # ---------------------------------------------

    if source_type == "jd_required_skill":

        return required_skill_exists_in_jd(
            source_value,
            job_profile
        )

    # ---------------------------------------------
    # JD preferred skill
    # ---------------------------------------------

    if source_type == "jd_preferred_skill":

        return preferred_skill_exists_in_jd(
            source_value,
            job_profile
        )

    # ---------------------------------------------
    # JD responsibility
    # ---------------------------------------------

    if source_type == "jd_responsibility":

        return responsibility_exists_in_jd(
            source_value,
            job_profile
        )

    # ---------------------------------------------
    # Missing required skill
    # ---------------------------------------------

    if source_type == "gap_required_skill":

        if not required_skill_exists_in_jd(
            source_value,
            job_profile
        ):
            return False

        if skill_exists_in_resume(
            source_value,
            resume_profile
        ):
            return False

        return True

    return False


def validate_question_text(
    question: str,
    category: str,
    source_type: str,
    topic: str
):

    if not isinstance(question, str):
        return False

    question = question.strip()

    if not question:
        return False

    # Generic interview questions
    if contains_generic_question(question):
        return False

    # Any explicit experience claim is unsafe
    # unless we have verified actual experience.
    if contains_experience_claim(question):

        # Current resume model does not distinguish
        # proven project experience strongly enough.
        # Therefore reject these claims.
        return False

    # A single question must have one main technical topic.
    if contains_multiple_topics(
        question,
        topic
    ):
        return False

    # Gap questions must NEVER ask about experience.
    if category == "gap":
        if contains_experience_claim(question):
            return False

    # Resume skill questions must not turn
    # a listed skill into claimed experience.
    if source_type == "resume_skill":
        if contains_experience_claim(question):
            return False

    # Project questions cannot invent contribution,
    # role, technology usage, etc.
    if source_type == "resume_project":
        if contains_experience_claim(question):
            return False

    return True


def validate_question(
    question: dict,
    resume_profile: dict,
    job_profile: dict,
    match_result: dict
):

    if not isinstance(
        question,
        dict
    ):
        return False

    required_fields = [
        "question",
        "category",
        "topic",
        "difficulty",
        "reason",
        "source_type",
        "source_value"
    ]

    for field in required_fields:

        if field not in question:
            return False

    question_text = question["question"]
    category = question["category"]
    topic = question["topic"]
    difficulty = question["difficulty"]
    reason = question["reason"]
    source_type = question["source_type"]
    source_value = question["source_value"]

    if not all(
        isinstance(value, str)
        for value in [
            question_text,
            category,
            topic,
            difficulty,
            reason,
            source_type,
            source_value
        ]
    ):
        return False

    if category not in VALID_CATEGORIES:
        return False

    if difficulty not in VALID_DIFFICULTIES:
        return False

    if source_type not in VALID_SOURCE_TYPES:
        return False

    if not question_text.strip():
        return False

    if not topic.strip():
        return False

    if not reason.strip():
        return False

    if not source_value.strip():
        return False

    # Soft skills cannot be technical topics.
    if is_soft_skill(topic):

        if category in {
            "jd",
            "gap"
        }:
            return False

    # Gap must never use soft skills.
    if source_type == "gap_required_skill":

        if is_soft_skill(source_value):
            return False

    # Category/source consistency.
    if category == "resume":

        if source_type not in {
            "resume_skill",
            "resume_item"
        }:
            return False

    if category == "project":

        if source_type != "resume_project":
            return False

    if category == "jd":

        if source_type not in {
            "jd_required_skill",
            "jd_preferred_skill",
            "jd_responsibility"
        }:
            return False

    if category == "gap":

        if source_type != "gap_required_skill":
            return False

    # Question text quality.
    if not validate_question_text(
        question_text,
        category,
        source_type,
        topic
    ):
        return False

    # Most important check:
    # source must actually exist and topic must point
    # to that exact source.
    if not source_is_valid(
        question,
        resume_profile,
        job_profile
    ):
        return False

    return True


def validate_questions(
    questions: list,
    resume_profile: dict,
    job_profile: dict,
    match_result: dict
):

    if not isinstance(
        questions,
        list
    ):
        return []

    valid_questions = []

    seen = set()

    for question in questions:

        if not validate_question(
            question,
            resume_profile,
            job_profile,
            match_result
        ):
            continue

        normalized_question = normalize(
            question["question"]
        )

        if normalized_question in seen:
            continue

        seen.add(
            normalized_question
        )

        valid_questions.append(
            question
        )

    return valid_questions