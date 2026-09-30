from sqlalchemy import Column, Integer, String, JSON , Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class InterviewSessionQuestion(Base):
    __tablename__ = "interview_session_questions"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id"),
        nullable=False,
        index=True
    )

    question = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    sequence_number = Column(Integer, nullable=False)
    ideal_answer = Column(Text, nullable=True)

    expected_concepts = Column(JSON, nullable=True)

    session = relationship(
        "InterviewSession",
        back_populates="session_questions"
    )