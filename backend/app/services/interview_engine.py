from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.attempt import Attempt


def get_next_difficulty(score: float, current_difficulty: str):
    current_difficulty = current_difficulty.lower()

    if score >= 80:
        if current_difficulty == "easy":
            return "Medium"

        if current_difficulty == "medium":
            return "Hard"

        return "Hard"

    if score < 50:
        if current_difficulty == "hard":
            return "Medium"

        if current_difficulty == "medium":
            return "Easy"

        return "Easy"

    if current_difficulty == "easy":
        return "Easy"

    if current_difficulty == "medium":
        return "Medium"

    return "Hard"


def get_attempted_question_ids(
    db: Session,
    session_id: int
):
    attempts = (
        db.query(Attempt)
        .filter(Attempt.session_id == session_id)
        .all()
    )

    return [
        attempt.question_id
        for attempt in attempts
        if attempt.question_id is not None
    ]


def get_attempted_session_question_ids(
    db: Session,
    session_id: int
):
    attempts = (
        db.query(Attempt)
        .filter(Attempt.session_id == session_id)
        .all()
    )

    return [
        attempt.session_question_id
        for attempt in attempts
        if attempt.session_question_id is not None
    ]


def find_question_by_missing_concept(
    db: Session,
    session,
    attempted_question_ids: list,
    missing_concepts: list | None = None
):
    if not missing_concepts:
        return None

    query = db.query(Question).filter(
        Question.topic == session.topic
    )

    if attempted_question_ids:
        query = query.filter(
            ~Question.id.in_(attempted_question_ids)
        )

    questions = query.all()

    for concept in missing_concepts:
        concept = concept.lower().strip()

        for question in questions:
            question_text = question.question.lower()
            ideal_answer = question.ideal_answer.lower()

            if (
                concept in question_text
                or concept in ideal_answer
            ):
                return question

    return None


def find_question_by_difficulty(
    db: Session,
    session,
    attempted_question_ids: list,
    difficulty: str
):
    query = db.query(Question).filter(
        Question.topic == session.topic,
        Question.difficulty == difficulty
    )

    if attempted_question_ids:
        query = query.filter(
            ~Question.id.in_(attempted_question_ids)
        )

    return query.first()


def find_any_question(
    db: Session,
    session,
    attempted_question_ids: list
):
    query = db.query(Question).filter(
        Question.topic == session.topic
    )

    if attempted_question_ids:
        query = query.filter(
            ~Question.id.in_(attempted_question_ids)
        )

    return query.first()


def select_next_question(
    db: Session,
    session,
    score: float | None = None,
    missing_concepts: list | None = None
):
    """
    Generic interview adaptive question selection.

    Flow:
    1. Check question limit.
    2. Adapt difficulty using previous score.
    3. Prefer a question related to missing concepts.
    4. Otherwise select matching difficulty.
    5. Otherwise select any unattempted question.
    """

    attempted_question_ids = get_attempted_question_ids(
        db,
        session.id
    )

    if len(attempted_question_ids) >= session.total_questions:
        return None

    if score is not None:
        next_difficulty = get_next_difficulty(
            score,
            session.difficulty
        )

        session.difficulty = next_difficulty

    question = find_question_by_missing_concept(
        db,
        session,
        attempted_question_ids,
        missing_concepts
    )

    if question:
        return question

    question = find_question_by_difficulty(
        db,
        session,
        attempted_question_ids,
        session.difficulty
    )

    if question:
        return question

    return find_any_question(
        db,
        session,
        attempted_question_ids
    )


def get_adaptive_strategy(
    score: float,
    missing_concepts: list | None = None
):
    """
    Decide what the next personalized question should focus on.
    """

    missing_concepts = missing_concepts or []

    if score < 50:
        return {
            "level": "reinforcement",
            "focus": "weak_area",
            "reason": "Previous answer needs improvement. The next question should reinforce the weak area.",
            "missing_concepts": missing_concepts
        }

    if score < 80:
        return {
            "level": "follow_up",
            "focus": "same_or_related_area",
            "reason": "Previous answer shows partial understanding. The next question should probe the same or a closely related concept.",
            "missing_concepts": missing_concepts
        }

    return {
        "level": "progression",
        "focus": "advanced_or_related_area",
        "reason": "Previous answer demonstrates strong understanding. The next question can move toward a more advanced or related concept.",
        "missing_concepts": missing_concepts
    }