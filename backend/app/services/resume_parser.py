import json
import re

from pypdf import PdfReader
from ollama import Client

from app.services.llm import OLLAMA_MODEL, OLLAMA_BASE_URL


# ---------------------------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------------------------

def extract_text_from_pdf(file_path: str):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


# ---------------------------------------------------------
# CLEAN LLM JSON RESPONSE
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DETERMINISTIC SKILL DETECTION
# ---------------------------------------------------------

def extract_known_skills(text: str):

    skill_dictionary = [

        # Programming Languages
        "Python",
        "C++",
        "Java",
        "JavaScript",

        # Web Technologies
        "HTML",
        "CSS",

        # Databases / Query Languages
        "SQL",
        "PostgreSQL",
        "MySQL",
        "MongoDB",

        # Data Science / ML
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",

        "Machine Learning",
        "Deep Learning",

        "Natural Language Processing",
        "NLP",

        "Generative AI",

        # LLM / GenAI
        "LangChain",
        "LangGraph",

        # Backend
        "FastAPI",
        "Flask",
        "Django",

        # Developer Tools
        "Git",
        "GitHub",
        "Docker",

        "VS Code",

        # ML Libraries
        "XGBoost",
        "CatBoost",

        # Computer Vision
        "OpenCV",

        # Visualization
        "Matplotlib",
        "Seaborn",

        # Core / Technical Concepts
        "Data Structures",
        "Data Science",
        "Cyber Security"
    ]

    text_lower = text.lower()

    found_skills = []

    for skill in skill_dictionary:

        pattern = (
            r"\b"
            + re.escape(skill.lower())
            + r"\b"
        )

        if re.search(pattern, text_lower):

            found_skills.append(skill)

    return found_skills


# ---------------------------------------------------------
# CLEAN / VALIDATE RESUME PROFILE
# ---------------------------------------------------------

def clean_resume_profile(
    profile: dict,
    raw_text: str
):

    raw_text_lower = raw_text.lower()

    # -----------------------------------------------------
    # EXPERIENCE CLEANUP
    # -----------------------------------------------------

    experience = profile.get(
        "experience",
        []
    )

    invalid_experience_keywords = [
        "club",
        "society",
        "festival",
        "fest",
        "member",
        "membership",
        "college event",
        "student activity",
        "team member",
        "volunteer",
        "position of responsibility"
    ]

    cleaned_experience = []

    for item in experience:

        if not isinstance(item, str):
            continue

        item = item.strip()

        if not item:
            continue

        item_lower = item.lower()

        if any(
            keyword in item_lower
            for keyword in invalid_experience_keywords
        ):
            continue

        cleaned_experience.append(item)

    profile["experience"] = cleaned_experience


    # -----------------------------------------------------
    # LEADERSHIP CLEANUP
    # -----------------------------------------------------

    leadership = profile.get(
        "leadership",
        []
    )

    cleaned_leadership = []

    # If the resume contains an explicit
    # "Leadership Skills" section,
    # extract its actual bullet points directly
    # from the resume text.

    leadership_match = re.search(
        r"Leadership Skills\s*(.*?)(?=\n(?:Achievements|Positions of Responsibility|Soft Skills|Declaration)\b)",
        raw_text,
        re.IGNORECASE | re.DOTALL
    )

    if leadership_match:

        leadership_section = leadership_match.group(1)

        bullets = re.findall(
            r"•\s*(.+)",
            leadership_section
        )

        for bullet in bullets:

            bullet = bullet.strip()

            if bullet:
                cleaned_leadership.append(
                    bullet
                )

    else:

        # Fallback to LLM output if there is no
        # explicit Leadership Skills section.

        for item in leadership:

            if not isinstance(item, str):
                continue

            item = item.strip()

            if not item:
                continue

            if item.lower() in raw_text_lower:

                cleaned_leadership.append(
                    item
                )

    profile["leadership"] = list(
        dict.fromkeys(
            cleaned_leadership
        )
    )


    # -----------------------------------------------------
    # PROJECT CLEANUP
    # -----------------------------------------------------

    projects = profile.get(
        "projects",
        []
    )

    cleaned_projects = []

    for item in projects:

        if not isinstance(item, str):
            continue

        item = item.strip()

        if item:
            cleaned_projects.append(item)

    profile["projects"] = list(
        dict.fromkeys(
            cleaned_projects
        )
    )


    # -----------------------------------------------------
    # ACHIEVEMENTS CLEANUP
    # -----------------------------------------------------

    achievements = profile.get(
        "achievements",
        []
    )

    cleaned_achievements = []

    for item in achievements:

        if not isinstance(item, str):
            continue

        item = item.strip()

        if item:
            cleaned_achievements.append(item)

    profile["achievements"] = list(
        dict.fromkeys(
            cleaned_achievements
        )
    )


    # -----------------------------------------------------
    # CERTIFICATIONS CLEANUP
    # -----------------------------------------------------

    certifications = profile.get(
        "certifications",
        []
    )

    cleaned_certifications = []

    for item in certifications:

        if not isinstance(item, str):
            continue

        item = item.strip()

        if item:
            cleaned_certifications.append(item)

    profile["certifications"] = list(
        dict.fromkeys(
            cleaned_certifications
        )
    )


    return profile


# ---------------------------------------------------------
# LLM RESUME EXTRACTION
# ---------------------------------------------------------

def extract_resume_profile(text: str):

    client = Client(
        host=OLLAMA_BASE_URL
    )

    prompt = f"""
You are a strict resume information extraction system.

Your task is to extract information ONLY from the
resume text provided below.

NEVER invent information.

NEVER infer information.

NEVER create information that is not explicitly
present in the resume.

NEVER add generic statements.

NEVER rewrite information into new claims.

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "skills": [],
    "projects": [],
    "experience": [],
    "education": [],
    "achievements": [],
    "leadership": [],
    "certifications": []
}}


=========================================================
SKILLS
=========================================================

Extract technical skills explicitly mentioned
in the resume.

Include:

- programming languages
- libraries
- frameworks
- databases
- AI/ML technologies
- developer tools
- software tools
- technical concepts

Each skill must be a separate item.

Do NOT infer related skills.

For example:

If the resume contains:

"Data Science"

DO NOT automatically add:

"Machine Learning"
"Pandas"
"NumPy"
"Scikit-learn"

unless they are explicitly present.

Do not treat one skill as another skill.

For example:

"JavaScript" does NOT mean "Java".

"Data Science" does NOT automatically mean
"Machine Learning".


=========================================================
PROJECTS
=========================================================

Extract only projects explicitly mentioned
in the resume.

Use the project name as written in the resume.

Do not invent projects.

Do not create project descriptions
that are not explicitly present.


=========================================================
EXPERIENCE
=========================================================

Only include actual professional experience such as:

- internships
- jobs
- employment
- professional work experience

DO NOT include:

- clubs
- societies
- college festivals
- memberships
- team participation
- student activities
- positions of responsibility
- volunteering unless it is clearly professional work

If there is no actual professional experience,
return:

[]


=========================================================
EDUCATION
=========================================================

Extract explicitly mentioned:

- degree
- institution
- field
- graduation information
- GPA
- CGPA

Do not invent missing educational information.


=========================================================
ACHIEVEMENTS
=========================================================

Extract explicitly mentioned:

- awards
- competition wins
- scholarships
- ranks
- honors
- achievements

Do not invent achievements.


=========================================================
LEADERSHIP
=========================================================

Extract leadership information only when it is
explicitly present in the resume.

If the resume contains a section such as:

"Leadership Skills"

extract the actual leadership statements
from that section.

DO NOT generate new leadership statements.

DO NOT convert:

- club membership
- society membership
- festival participation
- team membership

into leadership unless the resume explicitly
describes it as a leadership role.


=========================================================
CERTIFICATIONS
=========================================================

Extract only certifications explicitly mentioned.

Do not invent certifications.


=========================================================
IMPORTANT ANTI-HALLUCINATION RULE
=========================================================

Every extracted item must be supported by the
resume text.

If information is not present, return [].

Do not guess.

Do not infer.

Do not embellish.

Do not generate generic professional statements.


=========================================================
DUPLICATES
=========================================================

Do not duplicate information.

Keep each item only once.


=========================================================
RESUME TEXT
=========================================================

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

    content = clean_json_response(
        content
    )

    try:

        profile = json.loads(
            content
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Ollama returned invalid JSON while parsing resume"
        ) from error

    if not isinstance(profile, dict):

        raise RuntimeError(
            "Ollama returned an invalid resume profile"
        )

    return profile


# ---------------------------------------------------------
# MAIN RESUME PARSER
# ---------------------------------------------------------

def parse_resume(file_path: str):

    # -----------------------------------------------------
    # STEP 1: Extract PDF text
    # -----------------------------------------------------

    text = extract_text_from_pdf(
        file_path
    )

    if not text:

        raise RuntimeError(
            "No readable text found in resume"
        )


    # -----------------------------------------------------
    # STEP 2: Deterministic skill detection
    # -----------------------------------------------------

    detected_skills = extract_known_skills(
        text
    )


    # -----------------------------------------------------
    # STEP 3: LLM structured extraction
    # -----------------------------------------------------

    profile = extract_resume_profile(
        text
    )


    # -----------------------------------------------------
    # STEP 4: Clean / validate LLM output
    # -----------------------------------------------------

    profile = clean_resume_profile(
        profile,
        text
    )


    # -----------------------------------------------------
    # STEP 5: Merge skills
    # -----------------------------------------------------

    llm_skills = profile.get(
        "skills",
        []
    )

    combined_skills = (
        llm_skills
        + detected_skills
    )


    # -----------------------------------------------------
    # STEP 6: Remove duplicate skills
    # -----------------------------------------------------

    cleaned_skills = []

    seen_skills = set()

    for skill in combined_skills:

        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        if not skill:
            continue

        normalized_skill = skill.lower()

        if normalized_skill not in seen_skills:

            seen_skills.add(
                normalized_skill
            )

            cleaned_skills.append(
                skill
            )

    profile["skills"] = cleaned_skills


    # -----------------------------------------------------
    # STEP 7: Ensure all expected fields exist
    # -----------------------------------------------------

    profile.setdefault(
        "skills",
        []
    )

    profile.setdefault(
        "projects",
        []
    )

    profile.setdefault(
        "experience",
        []
    )

    profile.setdefault(
        "education",
        []
    )

    profile.setdefault(
        "achievements",
        []
    )

    profile.setdefault(
        "leadership",
        []
    )

    profile.setdefault(
        "certifications",
        []
    )


    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {
        "text": text,
        "profile": profile
    }