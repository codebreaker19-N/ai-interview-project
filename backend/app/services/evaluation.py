import logging
import re
from typing import Any, Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.llm import generate_suggested_answer
from app.services.tavily_service import search_technical_context
from app.rag.retrieval.retrieval_pipeline import RetrievalPipeline
from app.rag.context.context_builder import ContextBuilder



logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_STORE_PATH = "data/vector_store"

RETRIEVAL_TOP_K = 10
RERANK_TOP_K = 5
FINAL_TOP_K = 3

RELEVANCE_THRESHOLD = 0.0
MMR_LAMBDA = 0.7


# ============================================================
# RAG SINGLETONS
# ============================================================

_retrieval_pipeline = None
_context_builder = None


def get_retrieval_pipeline():
    global _retrieval_pipeline

    if _retrieval_pipeline is None:
        _retrieval_pipeline = RetrievalPipeline(
            vector_store_path=VECTOR_STORE_PATH,
            retrieval_top_k=RETRIEVAL_TOP_K,
            rerank_top_k=RERANK_TOP_K,
            final_top_k=FINAL_TOP_K,
            relevance_threshold=RELEVANCE_THRESHOLD,
            mmr_lambda=MMR_LAMBDA,
        )

    return _retrieval_pipeline


def get_context_builder():
    global _context_builder

    if _context_builder is None:
        _context_builder = ContextBuilder()

    return _context_builder


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = str(text).lower().strip()

    text = re.sub(
        r"[^a-z0-9+#./*\- ]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# KEYWORD COVERAGE
# ============================================================

def keyword_coverage(
    user_answer: str,
    ideal_answer: str,
) -> float:

    user_words = set(
        re.findall(
            r"\b\w+\b",
            user_answer.lower(),
        )
    )

    ideal_words = set(
        re.findall(
            r"\b\w+\b",
            ideal_answer.lower(),
        )
    )

    if not ideal_words:
        return 0.0

    matched_words = user_words.intersection(
        ideal_words
    )

    coverage = (
        len(matched_words)
        / len(ideal_words)
    )

    return float(
        round(
            coverage * 100,
            2,
        )
    )


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def semantic_similarity(
    user_answer: str,
    ideal_answer: str,
) -> float:

    if not user_answer or not user_answer.strip():
        return 0.0

    if not ideal_answer or not ideal_answer.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer()

        vectors = vectorizer.fit_transform(
            [
                user_answer,
                ideal_answer,
            ]
        )

        similarity = cosine_similarity(
            vectors[0],
            vectors[1],
        )[0][0]

        return float(
            round(
                float(similarity) * 100,
                2,
            )
        )

    except Exception as e:
        logger.exception(
            "Semantic similarity calculation failed: %s",
            e,
        )
        return 0.0


# ============================================================
# CONCEPT NORMALIZATION
# ============================================================

def normalize_concept(
    concept: str,
) -> str:

    return normalize_text(
        str(concept)
    )


# ============================================================
# CONCEPT MATCHING
# ============================================================

def match_expected_concepts(
    user_answer: str,
    expected_concepts: List[Any],
):

    normalized_answer = normalize_text(
        user_answer
    )

    covered = []
    missing = []

    for concept in expected_concepts:

        if concept is None:
            continue

        normalized_concept = normalize_concept(
            concept
        )

        if not normalized_concept:
            continue

        # ----------------------------------------------------
        # DIRECT PHRASE MATCH
        # ----------------------------------------------------

        if normalized_concept in normalized_answer:
            covered.append(concept)
            continue

        # ----------------------------------------------------
        # WORD LEVEL MATCH
        # ----------------------------------------------------

        concept_words = (
            normalized_concept.split()
        )

        if len(concept_words) > 1:

            matched_words = sum(
                1
                for word in concept_words
                if word in normalized_answer
            )

            if (
                matched_words
                / len(concept_words)
                >= 0.6
            ):
                covered.append(concept)
                continue

        # ----------------------------------------------------
        # SINGLE WORD MATCH
        # ----------------------------------------------------

        if len(concept_words) == 1:

            pattern = (
                r"\b"
                + re.escape(
                    concept_words[0]
                )
                + r"\b"
            )

            if re.search(
                pattern,
                normalized_answer,
            ):
                covered.append(concept)
                continue

        missing.append(concept)

    return covered, missing


# ============================================================
# CONCEPT COVERAGE
# ============================================================

def expected_concept_coverage(
    user_answer: str,
    expected_concepts: List[Any],
):

    if not expected_concepts:
        return 0.0, [], []

    covered, missing = match_expected_concepts(
        user_answer,
        expected_concepts,
    )

    total = len(expected_concepts)

    score = (
        len(covered)
        / total
    ) * 100

    return (
        float(round(score, 2)),
        covered,
        missing,
    )


# ============================================================
# TECHNICAL ACCURACY
# ============================================================

def technical_accuracy(
    semantic_similarity_score: float,
    keyword_coverage_score: float,
    concept_coverage_score_value: float,
):

    score = (
        float(semantic_similarity_score) * 0.30
        + float(keyword_coverage_score) * 0.20
        + float(concept_coverage_score_value) * 0.50
    )

    return float(
        round(score, 2)
    )


# ============================================================
# STRENGTHS
# ============================================================

def generate_strengths(
    concept_score: float,
    similarity_score: float,
    keyword_score: float,
):

    strengths = []

    if concept_score >= 80:
        strengths.append(
            "Strong coverage of expected technical concepts"
        )
    elif concept_score >= 60:
        strengths.append(
            "Good coverage of the main expected concepts"
        )

    if similarity_score >= 70:
        strengths.append(
            "Answer is semantically aligned with the expected answer"
        )

    if keyword_score >= 70:
        strengths.append(
            "Good coverage of relevant technical terminology"
        )

    if not strengths:
        strengths.append(
            "Answer attempts to address the question"
        )

    return strengths


# ============================================================
# WEAKNESSES
# ============================================================

def generate_weaknesses(
    concept_score: float,
    similarity_score: float,
    missing_concepts: List[Any],
):

    weaknesses = []

    if concept_score < 50:
        weaknesses.append(
            "Several important expected concepts are missing"
        )
    elif concept_score < 80:
        weaknesses.append(
            "Some expected technical concepts are missing"
        )

    if similarity_score < 50:
        weaknesses.append(
            "Answer has limited semantic overlap with the expected answer"
        )

    if missing_concepts:
        weaknesses.append(
            "Some important areas could be explained in more depth"
        )

    return weaknesses


# ============================================================
# COMMUNICATION
# ============================================================

def communication_score(
    user_answer: str,
):

    words = user_answer.split()

    if not words:
        return 0.0

    word_count = len(words)

    if word_count < 10:
        return 40.0

    if word_count <= 100:
        return 90.0

    return 70.0


# ============================================================
# CONFIDENCE
# ============================================================

def confidence_score(
    user_answer: str,
):

    words = user_answer.split()

    if not words:
        return 0.0

    word_count = len(words)

    if word_count < 5:
        return 30.0

    if word_count < 15:
        return 60.0

    return 85.0


# ============================================================
# FINAL SCORE
# ============================================================

def final_score(
    technical_accuracy_score: float,
    communication: float,
    confidence: float,
):

    score = (
        float(technical_accuracy_score) * 0.70
        + float(communication) * 0.20
        + float(confidence) * 0.10
    )

    return float(
        round(score, 2)
    )


# ============================================================
# TAVILY QUERY
# ============================================================

def build_tavily_query(
    ideal_answer: str,
    missing_concepts: List[Any],
):

    concepts = ", ".join(
        str(concept)
        for concept in missing_concepts
    )

    return (
        "technical interview explanation "
        "for the following concepts: "
        f"{concepts}. "
        "Reference topic: "
        f"{ideal_answer[:500]}"
    )


# ============================================================
# TAVILY CONTEXT
# ============================================================

def get_technical_context(
    ideal_answer: str,
    missing_concepts: List[Any],
):

    if not missing_concepts:
        return ""

    try:

        query = build_tavily_query(
            ideal_answer,
            missing_concepts,
        )

        result = search_technical_context(
            query
        )

        if not result:
            return ""

        context_parts = []

        answer = result.get(
            "answer"
        )

        if answer:
            context_parts.append(
                answer
            )

        results = result.get(
            "results",
            [],
        )

        for item in results[:3]:

            title = item.get(
                "title",
                "",
            )

            content = item.get(
                "content",
                "",
            )

            if content:
                context_parts.append(
                    f"{title}\n{content}"
                )

        return "\n\n".join(
            context_parts
        )

    except Exception as e:

        logger.exception(
            "Tavily technical context failed: %s",
            e,
        )

        return ""


# ============================================================
# RAG QUERY
# ============================================================

def build_rag_query(
    question: str,
    candidate_answer: str,
    expected_concepts: List[Any],
    missing_concepts: List[Any],
):

    expected = ", ".join(
        str(x)
        for x in expected_concepts
    )

    missing = ", ".join(
        str(x)
        for x in missing_concepts
    )

    return f"""
Interview Question:

{question}

Candidate Answer:

{candidate_answer}

Expected Concepts:

{expected}

Missing Concepts:

{missing}

Retrieve reliable technical knowledge relevant to
evaluating this interview answer.
""".strip()


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_rag_context(
    question: str,
    candidate_answer: str,
    expected_concepts: List[Any],
    missing_concepts: List[Any],
    candidate_profile: Optional[Dict[str, Any]] = None,
):

    query = build_rag_query(
        question=question,
        candidate_answer=candidate_answer,
        expected_concepts=expected_concepts,
        missing_concepts=missing_concepts,
    )

    empty_context = {
        "question": question,
        "candidate_answer": candidate_answer,
        "candidate_profile": candidate_profile or {},
        "retrieved_evidence": [],
    }

    try:

        pipeline = get_retrieval_pipeline()

        retrieved_results = pipeline.retrieve(
            query
        )

        if not retrieved_results:

            return {
                "query": query,
                "results": [],
                "context": empty_context,
            }

        builder = get_context_builder()

        context = builder.build(
            question=question,
            candidate_answer=candidate_answer,
            retrieved_results=retrieved_results,
            candidate_profile=candidate_profile,
        )

        return {
            "query": query,
            "results": retrieved_results,
            "context": context,
        }

    except Exception as e:

        logger.exception(
            "RAG retrieval failed: %s",
            e,
        )

        return {
            "query": query,
            "results": [],
            "context": empty_context,
        }


# ============================================================
# RAG SOURCE EXTRACTION
# ============================================================

def extract_rag_sources(
    retrieved_results: List[Dict[str, Any]],
):

    sources = []

    for result in retrieved_results:

        metadata = result.get(
            "metadata",
            {},
        )

        sources.append(
            {
                "domain": metadata.get("domain"),
                "topic": metadata.get("topic"),
                "subtopic": metadata.get("subtopic"),
                "concept": metadata.get("concept"),
                "source": metadata.get("source"),
                "source_type": metadata.get("source_type"),
                "reranker_score": result.get(
                    "reranker_score"
                ),
                "retrieval_score": result.get(
                    "score"
                ),
            }
        )

    return sources


# ============================================================
# RAG CONTEXT FORMATTER
# ============================================================

def format_rag_context_for_llm(
    rag_context: Dict[str, Any],
):

    evidence = rag_context.get(
        "retrieved_evidence",
        [],
    )

    if not evidence:
        return ""

    context_parts = []

    for index, item in enumerate(
        evidence,
        start=1,
    ):

        keywords = item.get(
            "keywords",
            [],
        )

        if isinstance(keywords, str):
            keywords_text = keywords
        else:
            keywords_text = ", ".join(
                str(keyword)
                for keyword in keywords
            )

        part = f"""
Evidence {index}

Domain:
{item.get("domain")}

Topic:
{item.get("topic")}

Subtopic:
{item.get("subtopic")}

Concept:
{item.get("concept")}

Content:
{item.get("content")}

Ideal Answer:
{item.get("ideal_answer")}

Keywords:
{keywords_text}

Source:
{item.get("source")}
""".strip()

        context_parts.append(
            part
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# GROUNDED SUGGESTED ANSWER
# ============================================================

def generate_grounded_suggested_answer(
    question: str,
    user_answer: str,
    ideal_answer: str,
    rag_context: Dict[str, Any],
    technical_context: str = "",
):

    formatted_rag = (
        format_rag_context_for_llm(
            rag_context
        )
    )

    prompt_context = f"""
You are an expert interview answer evaluator.

Interview Question:

{question}

Candidate Answer:

{user_answer}

Reference Ideal Answer:

{ideal_answer}

Additional Technical Context from Trusted RAG Sources:

{formatted_rag}

Additional Technical Context from Web Search:

{technical_context}

Task:

Create a concise, technically accurate improved answer
that the candidate could give in an interview.

Rules:

1. Use the trusted retrieved evidence when relevant.
2. Do not invent technical facts.
3. Do not blindly copy the reference answer.
4. Correct important technical gaps.
5. Include missing concepts when they are relevant.
6. Keep the answer natural and interview-friendly.
7. Do not mention RAG, retrieval, vector database,
   Tavily, or internal evaluation systems.
8. Do not claim unsupported facts.
9. Answer the actual interview question.
""".strip()

    try:

        return generate_suggested_answer(
            user_answer=user_answer,
            ideal_answer=ideal_answer,
            technical_context=prompt_context,
        )

    except Exception as e:

        logger.exception(
            "Suggested answer generation failed: %s",
            e,
        )

        return ideal_answer


# ============================================================
# MAIN EVALUATION
# ============================================================

def evaluate_answer(
    question: str,
    user_answer: str,
    ideal_answer: str,
    expected_concepts=None,
    candidate_profile=None,
):

    expected_concepts = (
        expected_concepts
        or []
    )

    # ========================================================
    # BASIC ML/NLP EVALUATION
    # ========================================================

    similarity = semantic_similarity(
        user_answer,
        ideal_answer,
    )

    coverage = keyword_coverage(
        user_answer,
        ideal_answer,
    )

    (
        concept_coverage,
        covered_concepts,
        missing_concepts,
    ) = expected_concept_coverage(
        user_answer,
        expected_concepts,
    )

    accuracy = technical_accuracy(
        similarity,
        coverage,
        concept_coverage,
    )

    strengths = generate_strengths(
        concept_coverage,
        similarity,
        coverage,
    )

    weaknesses = generate_weaknesses(
        concept_coverage,
        similarity,
        missing_concepts,
    )

    communication = communication_score(
        user_answer
    )

    confidence = confidence_score(
        user_answer
    )

    score = final_score(
        accuracy,
        communication,
        confidence,
    )

    # ========================================================
    # RAG
    # ========================================================

    rag_data = retrieve_rag_context(
        question=question,
        candidate_answer=user_answer,
        expected_concepts=expected_concepts,
        missing_concepts=missing_concepts,
        candidate_profile=candidate_profile,
    )

    rag_context = rag_data.get(
        "context",
        {},
    )

    retrieved_results = rag_data.get(
        "results",
        [],
    )

    # ========================================================
    # TAVILY
    # ========================================================

    technical_context = get_technical_context(
        ideal_answer=ideal_answer,
        missing_concepts=missing_concepts,
    )

    # ========================================================
    # GROUNDED SUGGESTED ANSWER
    # ========================================================

    suggested_answer = (
        generate_grounded_suggested_answer(
            question=question,
            user_answer=user_answer,
            ideal_answer=ideal_answer,
            rag_context=rag_context,
            technical_context=technical_context,
        )
    )

    # ========================================================
    # RAG SOURCES
    # ========================================================

    rag_sources = extract_rag_sources(
        retrieved_results
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "score": float(score),
        "overall_score": float(score),

        "technical_accuracy": float(
            accuracy
        ),

        "semantic_similarity": float(
            similarity
        ),

        "keyword_coverage": float(
            coverage
        ),

        "concept_coverage": float(
            concept_coverage
        ),

        "communication": float(
            communication
        ),

        "confidence": float(
            confidence
        ),

        "missing_concepts": missing_concepts,

        "covered_concepts": covered_concepts,

        "strengths": strengths,

        "weaknesses": weaknesses,

        "suggested_answer": suggested_answer,

        "rag": {
            "query": rag_data.get(
                "query",
                "",
            ),
            "retrieved_documents": len(
                retrieved_results
            ),
            "sources": rag_sources,
        },

        "technical_context": technical_context,
    }