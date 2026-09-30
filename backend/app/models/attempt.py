from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id"),
        nullable=True
    )

    # For generic interview questions
    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=True
    )

    # For personalized interview questions
    session_question_id = Column(
        Integer,
        ForeignKey("interview_session_questions.id"),
        nullable=True
    )

    user_answer = Column(
        String,
        nullable=False
    )

    score = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    session = relationship(
        "InterviewSession",
        back_populates="attempts"
    )

    evaluation = relationship(
        "Evaluation",
        back_populates="attempt",
        uselist=False
    )

    session_question = relationship(
        "InterviewSessionQuestion"
    )