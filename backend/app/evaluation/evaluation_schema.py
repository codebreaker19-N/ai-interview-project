from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    NOT_RELEVANT = "NOT_RELEVANT"


class EvaluationResult(BaseModel):

    claim_status: ClaimStatus

    technical_accuracy: int = Field(
        ge=0,
        le=100
    )

    semantic_similarity: int = Field(
        ge=0,
        le=100
    )

    keyword_coverage: int = Field(
        ge=0,
        le=100
    )

    communication: int = Field(
        ge=0,
        le=100
    )

    confidence: int = Field(
        ge=0,
        le=100
    )

    strengths: List[str]

    weaknesses: List[str]

    missing_concepts: List[str]

    reasoning: str

    suggested_answer: str

    sources: List[str]