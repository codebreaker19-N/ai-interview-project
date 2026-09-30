from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationResponse
from app.utils.auth import get_current_user


router = APIRouter()


# ============================================================
# GET EVALUATION BY ATTEMPT
# ============================================================

@router.get(
    "/{attempt_id}",
    response_model=EvaluationResponse
)
def get_evaluation(
    attempt_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    evaluation = (
        db.query(Evaluation)
        .join(Evaluation.attempt)
        .filter(
            Evaluation.attempt_id == attempt_id
        )
        .first()
    )

    if evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )

    # ========================================================
    # USER OWNERSHIP CHECK
    # ========================================================

    if evaluation.attempt.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not allowed to access "
                "this evaluation"
            )
        )

    return evaluation