from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    ForeignKey,
    JSON,
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    attempt_id = Column(
        Integer,
        ForeignKey("attempts.id"),
        nullable=False,
        unique=True
    )

    technical_accuracy = Column(
        Float,
        nullable=True
    )

    semantic_similarity = Column(
        Float,
        nullable=True
    )

    keyword_coverage = Column(
        Float,
        nullable=True
    )

    concept_coverage = Column(
        Float,
        nullable=True
    )

    communication = Column(
        Float,
        nullable=True
    )

    confidence = Column(
        Float,
        nullable=True
    )

    overall_score = Column(
        Float,
        nullable=True
    )

    missing_concepts = Column(
        JSON,
        nullable=True
    )

    covered_concepts = Column(
        JSON,
        nullable=True
    )

    strengths = Column(
        JSON,
        nullable=True
    )

    weaknesses = Column(
        JSON,
        nullable=True
    )

    suggested_answer = Column(
        Text,
        nullable=True
    )

    rag = Column(
        JSON,
        nullable=True
    )

    technical_context = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    attempt = relationship(
        "Attempt",
        back_populates="evaluation"
    )