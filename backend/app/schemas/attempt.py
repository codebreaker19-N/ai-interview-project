from pydantic import BaseModel


class AttemptCreate(BaseModel):
    session_id: int

    question_id: int | None = None
    session_question_id: int | None = None

    user_answer: str


class AttemptResponse(BaseModel):
    id: int
    user_id: int
    session_id: int | None

    question_id: int | None
    session_question_id: int | None

    user_answer: str
    score: int | None

    class Config:
        from_attributes = True