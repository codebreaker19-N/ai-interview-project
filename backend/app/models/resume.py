from sqlalchemy import Column, Integer, ForeignKey, JSON, Text, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, nullable=False)
    projects = Column(JSON, nullable=False)
    experience = Column(JSON, nullable=False)
    education = Column(JSON, nullable=False)
    achievements = Column(JSON, nullable=False)
    leadership = Column(JSON, nullable=False)
    certifications = Column(JSON, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )