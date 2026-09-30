from pydantic import BaseModel


class QuestionCreate(BaseModel):
    topic: str
    difficulty: str
    question: str
    ideal_answer: str

class QuestionResponse(BaseModel):
    id: int
    topic: str
    difficulty: str
    question: str
    ideal_answer: str

    class Config:
        from_attributes = True

class QuestionUpdate(BaseModel):
    topic: str
    difficulty: str
    question: str
    ideal_answer: str

class InterviewQuestionResponse(BaseModel):
    id: int
    topic: str
    difficulty: str
    question: str

    class Config:
        from_attributes = True