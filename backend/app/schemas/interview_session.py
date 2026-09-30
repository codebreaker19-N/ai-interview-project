from pydantic import BaseModel


class InterviewSessionCreate(BaseModel):
    topic: str
    difficulty: str
    total_questions: int
    resume_id: int | None = None
    job_description_id: int | None = None


class InterviewSessionResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int | None
    job_description_id: int | None
    topic: str
    difficulty: str
    total_questions: int
    current_question: int
    status: str

    class Config:
        from_attributes = True

class InterviewReportResponse(BaseModel):
    session_id: int
    topic: str
    difficulty: str
    total_questions: int
    questions_attempted: int

    average_score: float
    average_technical_accuracy: float
    average_semantic_similarity: float
    average_keyword_coverage: float
    average_concept_coverage: float
    average_communication: float
    average_confidence: float

    strengths: list
    weaknesses: list

    class Config:
        from_attributes = True