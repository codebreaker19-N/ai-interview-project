from pydantic import BaseModel
from typing import Any


class EvaluationSource(BaseModel):
    domain: str | None = None
    topic: str | None = None
    subtopic: str | None = None
    concept: str | None = None
    source: str | None = None
    source_type: str | None = None
    reranker_score: float | None = None
    retrieval_score: float | None = None


class EvaluationRAGResponse(BaseModel):
    query: str | None = None
    retrieved_documents: int = 0
    sources: list[EvaluationSource] = []


class EvaluationResponse(BaseModel):
    id: int
    attempt_id: int

    technical_accuracy: float | None = None
    semantic_similarity: float | None = None
    keyword_coverage: float | None = None
    concept_coverage: float | None = None

    communication: float | None = None
    confidence: float | None = None
    overall_score: float | None = None

    missing_concepts: list | None = None
    covered_concepts: list | None = None

    strengths: list | None = None
    weaknesses: list | None = None

    suggested_answer: str | None = None

    rag: EvaluationRAGResponse | None = None

    technical_context: str | None = None

    class Config:
        from_attributes = True