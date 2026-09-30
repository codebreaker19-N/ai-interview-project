from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.attempt import Attempt
from app.models.question import Question
from app.models.evaluation import Evaluation
from app.models.interview_session import InterviewSession
from app.models.interview_session_question import (
    InterviewSessionQuestion
)

from app.schemas.attempt import (
    AttemptCreate,
    AttemptResponse
)

from app.services.evaluation import evaluate_answer
from app.services.interview_engine import get_next_difficulty
from app.utils.auth import get_current_user


router = APIRouter()


@router.post(
    "/",
    response_model=AttemptResponse
)
def create_attempt(
    attempt: AttemptCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ========================================================
    # GET SESSION
    # ========================================================

    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == attempt.session_id,
            InterviewSession.user_id == user_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    if session.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Interview session is not active"
        )

    if not attempt.user_answer or not attempt.user_answer.strip():
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty"
        )

    # ========================================================
    # QUESTION VARIABLES
    # ========================================================

    personalized_question = None
    generic_question = None

    question_text = ""
    ideal_answer = ""
    expected_concepts = []

    # ========================================================
    # PERSONALIZED QUESTION
    # ========================================================

    if attempt.session_question_id is not None:

        personalized_question = (
            db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.id
                == attempt.session_question_id,
                InterviewSessionQuestion.session_id
                == session.id
            )
            .first()
        )

        if personalized_question is None:
            raise HTTPException(
                status_code=404,
                detail="Personalized interview question not found"
            )

        question_text = (
            getattr(
                personalized_question,
                "question",
                None
            )
            or getattr(
                personalized_question,
                "question_text",
                None
            )
            or ""
        )

        ideal_answer = (
            personalized_question.ideal_answer
            or ""
        )

        expected_concepts = (
            personalized_question.expected_concepts
            or []
        )

        if not ideal_answer:
            raise HTTPException(
                status_code=500,
                detail="Ideal answer is missing for this personalized question"
            )

    # ========================================================
    # GENERIC QUESTION
    # ========================================================

    elif attempt.question_id is not None:

        generic_question = (
            db.query(Question)
            .filter(
                Question.id == attempt.question_id
            )
            .first()
        )

        if generic_question is None:
            raise HTTPException(
                status_code=404,
                detail="Question not found"
            )

        question_text = (
            getattr(
                generic_question,
                "question",
                None
            )
            or ""
        )

        ideal_answer = (
            generic_question.ideal_answer
            or ""
        )

        expected_concepts = (
            getattr(
                generic_question,
                "expected_concepts",
                None
            )
            or []
        )

        if not ideal_answer:
            raise HTTPException(
                status_code=500,
                detail="Ideal answer is missing for this question"
            )

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                "Either question_id or "
                "session_question_id is required"
            )
        )

    # ========================================================
    # PREVENT DUPLICATE ATTEMPT
    # ========================================================

    if attempt.session_question_id is not None:

        existing_attempt = (
            db.query(Attempt)
            .filter(
                Attempt.session_id == session.id,
                Attempt.session_question_id
                == attempt.session_question_id
            )
            .first()
        )

    else:

        existing_attempt = (
            db.query(Attempt)
            .filter(
                Attempt.session_id == session.id,
                Attempt.question_id
                == attempt.question_id
            )
            .first()
        )

    if existing_attempt is not None:
        raise HTTPException(
            status_code=400,
            detail="This question has already been attempted"
        )

    # ========================================================
    # CANDIDATE PROFILE
    # ========================================================

    candidate_profile = {
        "user_id": user_id,
        "session_id": session.id
    }

    # ========================================================
    # EVALUATE ANSWER
    # ========================================================

    try:

        result = evaluate_answer(
            question=question_text,
            user_answer=attempt.user_answer,
            ideal_answer=ideal_answer,
            expected_concepts=expected_concepts,
            candidate_profile=candidate_profile
        )

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Answer evaluation failed: {str(error)}"
        )

    # ========================================================
    # CREATE ATTEMPT
    # ========================================================

    new_attempt = Attempt(
        user_id=user_id,
        session_id=session.id,
        question_id=attempt.question_id,
        session_question_id=attempt.session_question_id,
        user_answer=attempt.user_answer.strip(),
        score=round(
            float(
                result.get(
                    "overall_score",
                    result.get("score", 0)
                )
            )
        )
    )

    db.add(new_attempt)
    db.flush()

    # ========================================================
    # CREATE EVALUATION
    # ========================================================

    evaluation = Evaluation(
    attempt_id=new_attempt.id,

    technical_accuracy=result.get(
        "technical_accuracy"
    ),

    semantic_similarity=result.get(
        "semantic_similarity"
    ),

    keyword_coverage=result.get(
        "keyword_coverage"
    ),

    concept_coverage=result.get(
        "concept_coverage"
    ),

    communication=result.get(
        "communication"
    ),

    confidence=result.get(
        "confidence"
    ),

    overall_score=result.get(
        "overall_score",
        result.get("score")
    ),

    missing_concepts=result.get(
        "missing_concepts",
        []
    ),

    strengths=result.get(
        "strengths",
        []
    ),

    weaknesses=result.get(
        "weaknesses",
        []
    ),

    suggested_answer=result.get(
        "suggested_answer"
    ),

    rag=result.get(
        "rag"
    ),

    technical_context=result.get(
        "technical_context"
    )
 )

    # ========================================================
    # GENERIC ADAPTIVE DIFFICULTY
    # ========================================================

    if personalized_question is None:

        current_score = float(
            result.get(
                "overall_score",
                result.get("score", 0)
            )
        )

        next_difficulty = get_next_difficulty(
            current_score,
            session.difficulty
        )

        session.difficulty = next_difficulty

    # ========================================================
    # SESSION PROGRESS
    # ========================================================

    session.current_question = (
        session.current_question + 1
    )

    total_attempts = (
        db.query(Attempt)
        .filter(
            Attempt.session_id == session.id
        )
        .count()
    )

    if total_attempts >= session.total_questions:

        session.status = "completed"

        session.completed_at = datetime.now(
            timezone.utc
        )

    # ========================================================
    # COMMIT EVERYTHING
    # ========================================================

    try:

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save evaluation: {str(error)}"
        )

    # ========================================================
    # REFRESH ATTEMPT
    # ========================================================

    db.refresh(new_attempt)

    return new_attempt