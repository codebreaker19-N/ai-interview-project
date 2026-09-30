from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.database.database import get_db
from app.models.question import Question
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate
)

router = APIRouter()


@router.post("/")
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db)
):
    new_question = Question(
        topic=question.topic,
        difficulty=question.difficulty,
        question=question.question,
        ideal_answer=question.ideal_answer
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return {
        "message": "Question created successfully",
        "question_id": new_question.id
    }


@router.get("/all")
def get_all_questions(
    db: Session = Depends(get_db)
):
    questions = db.query(Question).all()

    return {
        "count": len(questions),
        "questions": [
            {
                "id": q.id,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "question": q.question
            }
            for q in questions
        ]
    }


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    question = db.get(Question, question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    return question


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db)
):
    question = db.get(Question, question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    question.topic = question_data.topic
    question.difficulty = question_data.difficulty
    question.question = question_data.question
    question.ideal_answer = question_data.ideal_answer

    db.commit()
    db.refresh(question)

    return question

@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    question = db.get(Question, question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    db.delete(question)
    db.commit()

    return {
        "message": "Question deleted successfully"
    }
