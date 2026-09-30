import os
import json
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv
from app.evaluation.evaluation_schema import EvaluationResult

load_dotenv()


# ============================================================
# LLM CONFIGURATION
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
).lower()

# ------------------------------------------------------------
# OLLAMA
# ------------------------------------------------------------

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

# ------------------------------------------------------------
# GEMINI
# ------------------------------------------------------------

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

# ------------------------------------------------------------
# NEBIUS
# ------------------------------------------------------------

NEBIUS_API_KEY = os.getenv(
    "NEBIUS_API_KEY"
)

NEBIUS_BASE_URL = os.getenv(
    "NEBIUS_BASE_URL",
    "https://api.tokenfactory.nebius.com/v1/"
)

NEBIUS_MODEL = os.getenv(
    "NEBIUS_MODEL",
    "openai/gpt-oss-120b"
)


# ============================================================
# EVALUATION JSON SCHEMA
# ============================================================

EVALUATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {

        "technical_accuracy": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },

        "semantic_similarity": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },

        "keyword_coverage": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },

        "communication": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },

        "confidence": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },

        "strengths": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "weaknesses": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "missing_concepts": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "reasoning": {
            "type": "string"
        },

        "suggested_answer": {
            "type": "string"
        },

        "sources": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },

    "required": [
        "technical_accuracy",
        "semantic_similarity",
        "keyword_coverage",
        "communication",
        "confidence",
        "strengths",
        "weaknesses",
        "missing_concepts",
        "reasoning",
        "suggested_answer",
        "sources"
    ],

    "additionalProperties": False
}


# ============================================================
# RAG CONTEXT FORMATTER
# ============================================================

def format_rag_evidence(
    retrieved_evidence: Optional[List[Dict[str, Any]]]
) -> str:

    if not retrieved_evidence:
        return "No retrieved RAG evidence was available."

    sections = []

    for index, evidence in enumerate(
        retrieved_evidence,
        start=1
    ):

        domain = evidence.get(
            "domain",
            ""
        )

        topic = evidence.get(
            "topic",
            ""
        )

        subtopic = evidence.get(
            "subtopic",
            ""
        )

        concept = evidence.get(
            "concept",
            ""
        )

        content = evidence.get(
            "content",
            ""
        )

        ideal_answer = evidence.get(
            "ideal_answer",
            ""
        )

        keywords = evidence.get(
            "keywords",
            []
        )

        source = evidence.get(
            "source",
            ""
        )

        reranker_score = evidence.get(
            "reranker_score"
        )

        sections.append(
            f"""
------------------------------------------------------------
RETRIEVED EVIDENCE {index}
------------------------------------------------------------

Source:
{source}

Domain:
{domain}

Topic:
{topic}

Subtopic:
{subtopic}

Concept:
{concept}

Keywords:
{", ".join(map(str, keywords))}

Reranker Score:
{reranker_score}

Evidence Content:
{content}

Reference Ideal Answer:
{ideal_answer}
"""
        )

    return "\n".join(sections)


# ============================================================
# BUILD SUGGESTED ANSWER PROMPT
# ============================================================

def build_suggested_answer_prompt(
    user_answer: str,
    ideal_answer: str,
    technical_context: str = "",
    retrieved_evidence: Optional[List[Dict[str, Any]]] = None
) -> str:

    rag_context = format_rag_evidence(
        retrieved_evidence
    )

    external_context_section = ""

    if technical_context:

        external_context_section = f"""
============================================================
ADDITIONAL TECHNICAL CONTEXT FROM TRUSTED SOURCES
============================================================

{technical_context}

Use this information only when it is relevant.

Do not invent facts that are not supported by:
1. Candidate answer
2. Reference answer
3. Retrieved RAG evidence
4. Trusted technical context
"""

    return f"""
You are an expert AI Interview Coach.

Your job is to improve a candidate's interview answer.

============================================================
CANDIDATE ANSWER
============================================================

{user_answer}


============================================================
REFERENCE IDEAL ANSWER
============================================================

{ideal_answer}


============================================================
RETRIEVED RAG EVIDENCE
============================================================

{rag_context}


{external_context_section}


============================================================
INSTRUCTIONS
============================================================

Improve the candidate's answer into a technically accurate,
clear, concise and interview-ready response.

Rules:

1. Preserve correct ideas from the candidate.

2. Correct factual or technical mistakes.

3. Add important missing concepts when supported by the
   retrieved evidence or reference answer.

4. Prefer retrieved RAG evidence when it is directly relevant.

5. Do not blindly copy the reference answer.

6. Do not invent unsupported technical claims.

7. Do not mention RAG.

8. Do not mention Tavily.

9. Do not mention the evaluation pipeline.

10. Do not mention this prompt.

11. Make the response sound natural in a real interview.

12. Keep the answer concise but complete.

13. If the candidate's answer is already correct, improve
    clarity rather than unnecessarily changing the content.

Return ONLY the improved interview answer.
"""


# ============================================================
# OLLAMA GENERATION
# ============================================================

def generate_with_ollama(
    prompt: str,
    json_mode: bool = False
) -> str:

    try:

        from ollama import Client

        client = Client(
            host=OLLAMA_BASE_URL
        )

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        kwargs = {
            "model": OLLAMA_MODEL,
            "messages": messages
        }

        if json_mode:

            kwargs["format"] = EVALUATION_JSON_SCHEMA

            messages[0]["content"] = f"""
{prompt}

============================================================
FINAL OUTPUT REQUIREMENTS
============================================================

Return EXACTLY ONE JSON object.

Required fields:

technical_accuracy
semantic_similarity
keyword_coverage
communication
confidence
strengths
weaknesses
missing_concepts
reasoning
suggested_answer
sources

Rules:

- Score fields must be integers from 0 to 100.
- strengths must be an array of strings.
- weaknesses must be an array of strings.
- missing_concepts must be an array of strings.
- sources must be an array of strings.
- reasoning must be a string.
- suggested_answer must be a string.
- Return JSON only.
- Do not return markdown.
- Do not return ```json.
- Do not return an empty object.
"""

        response = client.chat(
            **kwargs
        )

        content = response["message"]["content"]

        if not content or not content.strip():

            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return content.strip()

    except Exception as error:

        raise RuntimeError(
            f"Ollama generation failed: {str(error)}"
        ) from error


# ============================================================
# GEMINI GENERATION
# ============================================================

def generate_with_gemini(
    prompt: str,
    json_mode: bool = False
) -> str:

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    try:

        from google import genai

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        final_prompt = prompt

        if json_mode:

            final_prompt = f"""
{prompt}

============================================================
FINAL OUTPUT REQUIREMENTS
============================================================

Return EXACTLY ONE JSON object.

Required fields:

technical_accuracy
semantic_similarity
keyword_coverage
communication
confidence
strengths
weaknesses
missing_concepts
reasoning
suggested_answer
sources

All score fields must be integers from 0 to 100.

All list fields must contain strings only.

Return JSON only.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=final_prompt
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text.strip()

    except Exception as error:

        raise RuntimeError(
            f"Gemini generation failed: {str(error)}"
        ) from error


# ============================================================
# NEBIUS GENERATION
# ============================================================

def generate_with_nebius(
    prompt: str,
    json_mode: bool = False
) -> str:

    if not NEBIUS_API_KEY:

        raise RuntimeError(
            "NEBIUS_API_KEY is not configured."
        )

    try:

        from openai import OpenAI

        client = OpenAI(
            api_key=NEBIUS_API_KEY,
            base_url=NEBIUS_BASE_URL
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI Interview Coach. "
                    "Follow the requested output format exactly."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        if json_mode:

            messages[1]["content"] = f"""
{prompt}

============================================================
FINAL JSON OUTPUT REQUIREMENTS
============================================================

Return EXACTLY ONE valid JSON object.

Required fields:

technical_accuracy
semantic_similarity
keyword_coverage
communication
confidence
strengths
weaknesses
missing_concepts
reasoning
suggested_answer
sources

Score fields:
- integer
- range 0 to 100

List fields:
- strengths
- weaknesses
- missing_concepts
- sources

All must be arrays of strings.

reasoning:
- string

suggested_answer:
- string

Return JSON only.
"""

        response = client.chat.completions.create(
            model=NEBIUS_MODEL,
            messages=messages,
            temperature=0.2
        )

        content = response.choices[0].message.content

        if not content or not content.strip():

            raise RuntimeError(
                "Nebius returned an empty response."
            )

        return content.strip()

    except Exception as error:

        raise RuntimeError(
            f"Nebius generation failed: {str(error)}"
        ) from error


# ============================================================
# GENERIC LLM GENERATION
# ============================================================

def generate_text(
    prompt: str,
    json_mode: bool = False
) -> str:

    if LLM_PROVIDER == "ollama":

        return generate_with_ollama(
            prompt,
            json_mode=json_mode
        )

    if LLM_PROVIDER == "gemini":

        return generate_with_gemini(
            prompt,
            json_mode=json_mode
        )

    if LLM_PROVIDER == "nebius":

        return generate_with_nebius(
            prompt,
            json_mode=json_mode
        )

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}"
    )


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_object(
    response: str
) -> dict:

    if not response:

        raise RuntimeError(
            "LLM returned an empty response."
        )

    response = response.strip()

    if response == "{}":

        raise RuntimeError(
            "LLM returned an empty JSON object."
        )

    # --------------------------------------------------------
    # REMOVE MARKDOWN FENCES
    # --------------------------------------------------------

    if response.startswith("```"):

        lines = response.splitlines()

        cleaned_lines = []

        for line in lines:

            stripped = line.strip()

            if stripped.startswith("```"):
                continue

            cleaned_lines.append(line)

        response = "\n".join(
            cleaned_lines
        ).strip()

    # --------------------------------------------------------
    # DIRECT JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            response
        )

        if (
            isinstance(parsed, dict)
            and parsed
        ):

            return parsed

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # EXTRACT JSON FROM TEXT
    # --------------------------------------------------------

    start = response.find("{")
    end = response.rfind("}")

    if (
        start != -1
        and end != -1
        and end > start
    ):

        json_text = response[
            start:end + 1
        ]

        try:

            parsed = json.loads(
                json_text
            )

            if (
                isinstance(parsed, dict)
                and parsed
            ):

                return parsed

        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        "LLM returned invalid JSON.\n\n"
        f"Raw response:\n{response}"
    )


# ============================================================
# SUGGESTED ANSWER
# ============================================================

def generate_suggested_answer(
    user_answer: str,
    ideal_answer: str,
    technical_context: str = "",
    retrieved_evidence: Optional[
        List[Dict[str, Any]]
    ] = None
) -> str:

    prompt = build_suggested_answer_prompt(
        user_answer=user_answer,
        ideal_answer=ideal_answer,
        technical_context=technical_context,
        retrieved_evidence=retrieved_evidence
    )

    return generate_text(
        prompt,
        json_mode=False
    )


# ============================================================
# STRUCTURED EVALUATION PROMPT
# ============================================================

def build_structured_evaluation_prompt(
    original_prompt: str,
    verification: Optional[
        Dict[str, Any]
    ] = None,
    technical_accuracy_baseline: Optional[int] = None,
    retrieved_evidence: Optional[
        List[Dict[str, Any]]
    ] = None
) -> str:

    verification = verification or {}

    overall_status = verification.get(
        "overall_status",
        "NOT_ENOUGH_EVIDENCE"
    )

    detected_concepts = verification.get(
        "detected_concepts",
        {}
    )

    claims = verification.get(
        "claims",
        []
    )

    supported_claims = verification.get(
        "supported_claims",
        []
    )

    partial_claims = verification.get(
        "partial_claims",
        []
    )

    contradicted_claims = verification.get(
        "contradicted_claims",
        []
    )

    unsupported_claims = verification.get(
        "unsupported_claims",
        []
    )

    allowed_sources = verification.get(
        "allowed_sources",
        []
    )

    if technical_accuracy_baseline is None:

        technical_accuracy_baseline = 50

    rag_context = format_rag_evidence(
        retrieved_evidence
    )

    verification_section = f"""

============================================================
RETRIEVED RAG EVIDENCE
============================================================

{rag_context}


============================================================
DETERMINISTIC CLAIM VERIFICATION
============================================================

Overall Status:
{overall_status}

Detected Concepts:
{json.dumps(
    detected_concepts,
    indent=2
)}

Claims:
{json.dumps(
    claims,
    indent=2
)}

Supported Claims:
{json.dumps(
    supported_claims,
    indent=2
)}

Partially Supported Claims:
{json.dumps(
    partial_claims,
    indent=2
)}

Contradicted Claims:
{json.dumps(
    contradicted_claims,
    indent=2
)}

Unsupported Claims:
{json.dumps(
    unsupported_claims,
    indent=2
)}


============================================================
AUTHORITATIVE TECHNICAL ACCURACY
============================================================

Technical Accuracy Baseline:
{technical_accuracy_baseline}

IMPORTANT:

The deterministic verification layer has calculated the
Technical Accuracy Baseline.

Treat this value as authoritative.

Return technical_accuracy EXACTLY equal to:

{technical_accuracy_baseline}

Do NOT recalculate it.

Do NOT increase it because semantic similarity is high.

Do NOT increase it because keyword coverage is high.

Do NOT infer correctness from terminology alone.

Do NOT override contradicted claims.


============================================================
CLAIM-LEVEL FEEDBACK
============================================================

STRENGTHS:

Mention only claims actually supported by the evidence.

WEAKNESSES:

Mention genuine missing concepts.

If a claim is contradicted, explicitly describe the
contradiction.

Do not describe a contradiction merely as a missing detail.

MISSING_CONCEPTS:

Include only relevant concepts that are absent or
insufficiently explained.

Do not invent concepts.

REASONING:

Explain the evaluation using the verification findings.

If there is a contradiction, explicitly explain it.

If the candidate is correct but concise, explain that
the core claims are supported.

SUGGESTED_ANSWER:

Provide a technically accurate interview-ready answer.

Do not repeat factual errors.

Use retrieved evidence when relevant.

SOURCES:

Only return identifiers that occur in the retrieved
evidence.

Allowed source identifiers:

{json.dumps(
    allowed_sources,
    indent=2
)}
"""

    return (
        f"{original_prompt}\n"
        f"{verification_section}"
    )


# ============================================================
# VALIDATE EVALUATION JSON
# ============================================================

def validate_evaluation_response(
    parsed_response: Dict[str, Any]
) -> None:

    required_fields = {
        "technical_accuracy",
        "semantic_similarity",
        "keyword_coverage",
        "communication",
        "confidence",
        "strengths",
        "weaknesses",
        "missing_concepts",
        "reasoning",
        "suggested_answer",
        "sources"
    }

    missing_fields = (
        required_fields
        - set(parsed_response.keys())
    )

    if missing_fields:

        raise RuntimeError(
            "LLM evaluation JSON is missing required fields.\n\n"
            f"Missing fields: "
            f"{sorted(missing_fields)}\n\n"
            f"Parsed response:\n"
            f"{parsed_response}"
        )

    # --------------------------------------------------------
    # SCORE VALIDATION
    # --------------------------------------------------------

    score_fields = [
        "technical_accuracy",
        "semantic_similarity",
        "keyword_coverage",
        "communication",
        "confidence"
    ]

    for field in score_fields:

        value = parsed_response.get(
            field
        )

        if isinstance(value, bool):

            raise RuntimeError(
                f"Evaluation field '{field}' "
                f"must be an integer."
            )

        if not isinstance(value, int):

            raise RuntimeError(
                f"Evaluation field '{field}' "
                f"must be an integer.\n\n"
                f"Received: {value}"
            )

        if not 0 <= value <= 100:

            raise RuntimeError(
                f"Evaluation field '{field}' "
                f"must be between 0 and 100.\n\n"
                f"Received: {value}"
            )

    # --------------------------------------------------------
    # LIST VALIDATION
    # --------------------------------------------------------

    list_fields = [
        "strengths",
        "weaknesses",
        "missing_concepts",
        "sources"
    ]

    for field in list_fields:

        value = parsed_response.get(
            field
        )

        if not isinstance(value, list):

            raise RuntimeError(
                f"Evaluation field '{field}' "
                f"must be a list."
            )

        for item in value:

            if not isinstance(item, str):

                raise RuntimeError(
                    f"Evaluation field '{field}' "
                    f"must contain strings only."
                )

    # --------------------------------------------------------
    # STRING VALIDATION
    # --------------------------------------------------------

    string_fields = [
        "reasoning",
        "suggested_answer"
    ]

    for field in string_fields:

        value = parsed_response.get(
            field
        )

        if not isinstance(value, str):

            raise RuntimeError(
                f"Evaluation field '{field}' "
                f"must be a string."
            )


# ============================================================
# ENFORCE DETERMINISTIC TECHNICAL ACCURACY
# ============================================================

def enforce_technical_accuracy(
    parsed_response: Dict[str, Any],
    technical_accuracy_baseline: Optional[int]
) -> Dict[str, Any]:

    if technical_accuracy_baseline is None:

        return parsed_response

    if not isinstance(
        technical_accuracy_baseline,
        int
    ):

        raise RuntimeError(
            "technical_accuracy_baseline "
            "must be an integer."
        )

    if not 0 <= technical_accuracy_baseline <= 100:

        raise RuntimeError(
            "technical_accuracy_baseline "
            "must be between 0 and 100."
        )

    parsed_response[
        "technical_accuracy"
    ] = technical_accuracy_baseline

    return parsed_response


# ============================================================
# SOURCE VALIDATION
# ============================================================

def validate_sources(
    parsed_response: Dict[str, Any],
    verification: Optional[
        Dict[str, Any]
    ]
) -> None:

    if verification is None:

        return

    allowed_sources = verification.get(
        "allowed_sources"
    )

    if allowed_sources is None:

        return

    allowed_sources = set(
        str(source)
        for source in allowed_sources
    )

    returned_sources = set(
        parsed_response.get(
            "sources",
            []
        )
    )

    invalid_sources = (
        returned_sources
        - allowed_sources
    )

    if invalid_sources:

        raise RuntimeError(
            "LLM returned source identifiers "
            "that were not present in retrieved evidence.\n\n"
            f"Invalid sources: "
            f"{sorted(invalid_sources)}\n\n"
            f"Allowed sources: "
            f"{sorted(allowed_sources)}"
        )


# ============================================================
# STRUCTURED EVALUATION
# ============================================================

def generate_evaluation(
    prompt: str,
    verification: Optional[
        Dict[str, Any]
    ] = None,
    technical_accuracy_baseline: Optional[int] = None,
    retrieved_evidence: Optional[
        List[Dict[str, Any]]
    ] = None
) -> EvaluationResult:

    # --------------------------------------------------------
    # BUILD FINAL PROMPT
    # --------------------------------------------------------

    final_prompt = build_structured_evaluation_prompt(
        original_prompt=prompt,
        verification=verification,
        technical_accuracy_baseline=
        technical_accuracy_baseline,
        retrieved_evidence=
        retrieved_evidence
    )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    response = generate_text(
        final_prompt,
        json_mode=True
    )

    # --------------------------------------------------------
    # EMPTY RESPONSE
    # --------------------------------------------------------

    if (
        not response
        or not response.strip()
    ):

        raise RuntimeError(
            "LLM returned an empty response."
        )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        parsed_response = extract_json_object(
            response
        )

    except Exception as error:

        raise RuntimeError(
            "Failed to parse LLM evaluation response.\n\n"
            f"Raw response:\n{response}\n\n"
            f"Error:\n{str(error)}"
        ) from error

    # --------------------------------------------------------
    # VALIDATE JSON
    # --------------------------------------------------------

    try:

        validate_evaluation_response(
            parsed_response
        )

    except Exception as error:

        raise RuntimeError(
            "Invalid LLM evaluation response.\n\n"
            f"Parsed response:\n"
            f"{parsed_response}\n\n"
            f"Error:\n{str(error)}"
        ) from error

    # --------------------------------------------------------
    # ENFORCE DETERMINISTIC ACCURACY
    # --------------------------------------------------------

    parsed_response = enforce_technical_accuracy(
        parsed_response,
        technical_accuracy_baseline
    )

    # --------------------------------------------------------
    # VALIDATE SOURCES
    # --------------------------------------------------------

    validate_sources(
        parsed_response,
        verification
    )

    # --------------------------------------------------------
    # PYDANTIC VALIDATION
    # --------------------------------------------------------

    try:

        evaluation = EvaluationResult(
            **parsed_response
        )

        return evaluation

    except Exception as error:

        raise RuntimeError(
            "Evaluation validation failed.\n\n"
            f"Parsed response:\n"
            f"{parsed_response}\n\n"
            f"Validation error:\n"
            f"{str(error)}"
        ) from error