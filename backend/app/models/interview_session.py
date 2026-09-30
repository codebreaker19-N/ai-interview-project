from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    resume_id = Column(
        Integer,
        ForeignKey("resume_profiles.id"),
        nullable=True
    )

    job_description_id = Column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=True
    )

    topic = Column(
        String,
        nullable=False
    )

    difficulty = Column(
        String,
        nullable=False
    )

    total_questions = Column(
        Integer,
        nullable=False
    )

    current_question = Column(
        Integer,
        default=1
    )

    status = Column(
        String,
        default="active"
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    attempts = relationship(
        "Attempt",
        back_populates="session"
    )

    session_questions = relationship(
        "InterviewSessionQuestion",
        back_populates="session",
        cascade="all, delete-orphan"
    )

