from sqlalchemy import Column, Integer, ForeignKey, JSON, Text, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    raw_text = Column(Text, nullable=False)

    required_skills = Column(JSON, nullable=False)
    responsibilities = Column(JSON, nullable=False)
    qualifications = Column(JSON, nullable=False)
    preferred_skills = Column(JSON, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )