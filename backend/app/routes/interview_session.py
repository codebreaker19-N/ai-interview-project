from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.interview_session import InterviewSession
from app.models.interview_session_question import InterviewSessionQuestion
from app.models.question import Question
from app.models.attempt import Attempt
from app.models.evaluation import Evaluation

from app.models.resume import ResumeProfile
from app.models.job_description import JobDescription

from app.schemas.interview_session import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewReportResponse
)

from app.schemas.question import InterviewQuestionResponse

from app.services.interview_engine import (
    get_attempted_question_ids,
    select_next_question
)

from app.services.resume_jd_matcher import match_resume_with_job

from app.services.personalized_question_generator import (
    generate_personalized_questions,
    generate_question_and_answer
)

from app.utils.auth import get_current_user


router = APIRouter()


# ============================================================
# CREATE INTERVIEW SESSION
# ============================================================

@router.post(
    "/session",
    response_model=InterviewSessionResponse
)
def create_session(
    session_data: InterviewSessionCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ========================================================
    # GENERIC INTERVIEW
    # ========================================================

    if (
        session_data.resume_id is None
        or session_data.job_description_id is None
    ):

        new_session = InterviewSession(
            user_id=user_id,
            topic=session_data.topic,
            difficulty=session_data.difficulty,
            total_questions=session_data.total_questions,
            current_question=1,
            status="active"
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return new_session

    # ========================================================
    # GET RESUME
    # ========================================================

    resume = (
        db.query(ResumeProfile)
        .filter(
            ResumeProfile.id == session_data.resume_id,
            ResumeProfile.user_id == user_id
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # ========================================================
    # GET JOB DESCRIPTION
    # ========================================================

    job_description = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == session_data.job_description_id,
            JobDescription.user_id == user_id
        )
        .first()
    )

    if job_description is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    # ========================================================
    # BUILD RESUME PROFILE
    # ========================================================

    resume_profile = {
        "skills": resume.skills,
        "projects": resume.projects,
        "experience": resume.experience,
        "education": resume.education,
        "achievements": resume.achievements,
        "leadership": resume.leadership,
        "certifications": resume.certifications
    }

    # ========================================================
    # BUILD JOB PROFILE
    # ========================================================

    job_profile = {
        "required_skills": job_description.required_skills,
        "preferred_skills": job_description.preferred_skills,
        "responsibilities": job_description.responsibilities,
        "qualifications": job_description.qualifications
    }

    # ========================================================
    # RESUME + JD MATCHING
    # ========================================================

    match_result = match_resume_with_job(
        resume_profile,
        job_profile
    )

    # ========================================================
    # GENERATE ONLY FIRST PERSONALIZED QUESTION
    # ========================================================

    try:

        generated = generate_personalized_questions(
            resume_profile=resume_profile,
            job_profile=job_profile,
            match_result=match_result,
            number_of_questions=1
        )

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {str(error)}"
        )

    questions = generated.get(
        "questions",
        []
    )

    if not questions:

        raise HTTPException(
            status_code=500,
            detail="No personalized question was generated"
        )

    # ========================================================
    # CREATE PERSONALIZED SESSION
    # ========================================================

    new_session = InterviewSession(
        user_id=user_id,
        resume_id=session_data.resume_id,
        job_description_id=session_data.job_description_id,
        topic="Personalized Interview",
        difficulty=session_data.difficulty,
        total_questions=session_data.total_questions,
        current_question=1,
        status="active"
    )

    db.add(new_session)
    db.flush()

    # ========================================================
    # SAVE FIRST PERSONALIZED QUESTION
    # ========================================================

    question_data = questions[0]

    session_question = InterviewSessionQuestion(
        session_id=new_session.id,
        question=question_data["question"],
        category=question_data["category"],
        topic=question_data["topic"],
        difficulty=question_data["difficulty"],
        reason=question_data.get("reason"),
        sequence_number=1,
        ideal_answer=question_data.get(
            "ideal_answer"
        ),
        expected_concepts=question_data.get(
            "expected_concepts",
            []
        )
    )

    db.add(session_question)

    # ========================================================
    # COMMIT
    # ========================================================

    try:

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save interview question: "
                f"{str(error)}"
            )
        )

    db.refresh(new_session)

    return new_session


# ============================================================
# GET CURRENT QUESTION
# ============================================================

@router.get(
    "/session/{session_id}/question",
    response_model=InterviewQuestionResponse
)
def get_current_question(
    session_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    session = db.get(
        InterviewSession,
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    if session.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this session"
        )

    if session.status != "active":

        raise HTTPException(
            status_code=400,
            detail="Interview session is not active"
        )

    # ========================================================
    # PERSONALIZED INTERVIEW
    # ========================================================

    if (
        session.resume_id is not None
        and session.job_description_id is not None
    ):

        session_question = (
            db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.session_id
                == session_id,
                InterviewSessionQuestion.sequence_number
                == session.current_question
            )
            .first()
        )

        if session_question is None:

            raise HTTPException(
                status_code=404,
                detail="No question available for this position"
            )

        return {
            "id": session_question.id,
            "topic": session_question.topic,
            "difficulty": session_question.difficulty,
            "question": session_question.question
        }

    # ========================================================
    # GENERIC INTERVIEW
    # ========================================================

    attempted_question_ids = get_attempted_question_ids(
        db,
        session_id
    )

    query = (
        db.query(Question)
        .filter(
            Question.topic == session.topic
        )
    )

    if attempted_question_ids:

        query = query.filter(
            ~Question.id.in_(
                attempted_question_ids
            )
        )

    question = (
        query
        .filter(
            Question.difficulty
            == session.difficulty
        )
        .first()
    )

    if question is None:
        question = query.first()

    if question is None:

        raise HTTPException(
            status_code=404,
            detail="No more questions available"
        )

    return question


# ============================================================
# GET SESSION DETAILS
# ============================================================

@router.get(
    "/session/{session_id}",
    response_model=InterviewSessionResponse
)
def get_session(
    session_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    session = db.get(
        InterviewSession,
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    if session.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this session"
        )

    return session


# ============================================================
# GET INTERVIEW REPORT
# ============================================================

@router.get(
    "/session/{session_id}/report",
    response_model=InterviewReportResponse
)
def get_interview_report(
    session_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    session = db.get(
        InterviewSession,
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    if session.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this session"
        )

    attempts = (
        db.query(Attempt)
        .filter(
            Attempt.session_id == session_id
        )
        .all()
    )

    if not attempts:

        raise HTTPException(
            status_code=404,
            detail="No attempts found for this session"
        )

    evaluations = []

    for attempt in attempts:

        evaluation = (
            db.query(Evaluation)
            .filter(
                Evaluation.attempt_id == attempt.id
            )
            .first()
        )

        if evaluation:
            evaluations.append(evaluation)

    if not evaluations:

        raise HTTPException(
            status_code=404,
            detail="No evaluations found for this session"
        )

    def average(values):

        if not values:
            return 0

        return round(
            sum(values) / len(values),
            2
        )

    average_score = average([
        evaluation.overall_score
        for evaluation in evaluations
        if evaluation.overall_score is not None
    ])

    average_technical_accuracy = average([
        evaluation.technical_accuracy
        for evaluation in evaluations
        if evaluation.technical_accuracy is not None
    ])

    average_semantic_similarity = average([
        evaluation.semantic_similarity
        for evaluation in evaluations
        if evaluation.semantic_similarity is not None
    ])

    average_keyword_coverage = average([
        evaluation.keyword_coverage
        for evaluation in evaluations
        if evaluation.keyword_coverage is not None
    ])

    average_concept_coverage = average([
        evaluation.concept_coverage
        for evaluation in evaluations
        if evaluation.concept_coverage is not None
    ])

    average_communication = average([
        evaluation.communication
        for evaluation in evaluations
        if evaluation.communication is not None
    ])

    average_confidence = average([
        evaluation.confidence
        for evaluation in evaluations
        if evaluation.confidence is not None
    ])

    strengths = []

    for evaluation in evaluations:

        if evaluation.strengths:
            strengths.extend(
                evaluation.strengths
            )

    weaknesses = []

    for evaluation in evaluations:

        if evaluation.weaknesses:
            weaknesses.extend(
                evaluation.weaknesses
            )

    return {
        "session_id": session.id,
        "topic": session.topic,
        "difficulty": session.difficulty,
        "total_questions": session.total_questions,
        "questions_attempted": len(attempts),
        "average_score": average_score,
        "average_technical_accuracy":
            average_technical_accuracy,
        "average_semantic_similarity":
            average_semantic_similarity,
        "average_keyword_coverage":
            average_keyword_coverage,
        "average_concept_coverage":
            average_concept_coverage,
        "average_communication":
            average_communication,
        "average_confidence":
            average_confidence,
        "strengths": strengths,
        "weaknesses": weaknesses
    }


# ============================================================
# GET NEXT QUESTION
# ============================================================

@router.get(
    "/session/{session_id}/next-question",
    response_model=InterviewQuestionResponse
)
def get_next_question(
    session_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    session = db.get(
        InterviewSession,
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    if session.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this session"
        )

    if session.status != "active":

        raise HTTPException(
            status_code=400,
            detail="Interview session is not active"
        )

    # ========================================================
    # PERSONALIZED INTERVIEW
    # ========================================================

    if (
        session.resume_id is not None
        and session.job_description_id is not None
    ):

        attempts = (
            db.query(Attempt)
            .filter(
                Attempt.session_id == session_id,
                Attempt.session_question_id.isnot(None)
            )
            .order_by(
                Attempt.id.desc()
            )
            .all()
        )

        # ----------------------------------------------------
        # SESSION LIMIT
        # ----------------------------------------------------

        if len(attempts) >= session.total_questions:

            session.status = "completed"

            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Interview session is completed"
            )

        # ----------------------------------------------------
        # NO PREVIOUS ATTEMPT
        # ----------------------------------------------------

        if not attempts:

            first_question = (
                db.query(InterviewSessionQuestion)
                .filter(
                    InterviewSessionQuestion.session_id
                    == session_id,
                    InterviewSessionQuestion.sequence_number
                    == 1
                )
                .first()
            )

            if first_question is None:

                raise HTTPException(
                    status_code=404,
                    detail="No personalized question available"
                )

            session.current_question = 1

            db.commit()

            return {
                "id": first_question.id,
                "topic": first_question.topic,
                "difficulty": first_question.difficulty,
                "question": first_question.question
            }

        # ----------------------------------------------------
        # LATEST ATTEMPT
        # ----------------------------------------------------

        latest_attempt = attempts[0]

        # ----------------------------------------------------
        # LATEST QUESTION
        # ----------------------------------------------------

        previous_question = None

        if latest_attempt.session_question_id is not None:

            previous_session_question = (
                db.query(InterviewSessionQuestion)
                .filter(
                    InterviewSessionQuestion.id
                    == latest_attempt.session_question_id,
                    InterviewSessionQuestion.session_id
                    == session_id
                )
                .first()
            )

            if previous_session_question:

                previous_question = (
                    previous_session_question.question
                )

        # ----------------------------------------------------
        # LATEST EVALUATION
        # ----------------------------------------------------

        latest_evaluation = (
            db.query(Evaluation)
            .filter(
                Evaluation.attempt_id
                == latest_attempt.id
            )
            .first()
        )

        if latest_evaluation is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Evaluation for the previous "
                    "answer not found"
                )
            )

        # ----------------------------------------------------
        # ADAPTIVE SIGNALS
        # ----------------------------------------------------

        latest_score = float(
            latest_evaluation.overall_score or 0
        )

        missing_concepts = (
            latest_evaluation.missing_concepts
            or []
        )

        # ----------------------------------------------------
        # GET RESUME
        # ----------------------------------------------------

        resume = (
            db.query(ResumeProfile)
            .filter(
                ResumeProfile.id == session.resume_id,
                ResumeProfile.user_id == user_id
            )
            .first()
        )

        if resume is None:

            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        # ----------------------------------------------------
        # GET JOB DESCRIPTION
        # ----------------------------------------------------

        job_description = (
            db.query(JobDescription)
            .filter(
                JobDescription.id
                == session.job_description_id,
                JobDescription.user_id
                == user_id
            )
            .first()
        )

        if job_description is None:

            raise HTTPException(
                status_code=404,
                detail="Job description not found"
            )

        # ----------------------------------------------------
        # BUILD RESUME PROFILE
        # ----------------------------------------------------

        resume_profile = {
            "skills": resume.skills,
            "projects": resume.projects,
            "experience": resume.experience,
            "education": resume.education,
            "achievements": resume.achievements,
            "leadership": resume.leadership,
            "certifications": resume.certifications
        }

        # ----------------------------------------------------
        # BUILD JOB PROFILE
        # ----------------------------------------------------

        job_profile = {
            "required_skills":
                job_description.required_skills,
            "preferred_skills":
                job_description.preferred_skills,
            "responsibilities":
                job_description.responsibilities,
            "qualifications":
                job_description.qualifications
        }

        # ----------------------------------------------------
        # RESUME + JD MATCHING
        # ----------------------------------------------------

        match_result = match_resume_with_job(
            resume_profile,
            job_profile
        )

        # ----------------------------------------------------
        # SELECT ADAPTIVE SOURCE
        # ----------------------------------------------------

        if missing_concepts:

            source_value = str(
                missing_concepts[0]
            )

            source_type = "missing_concept"

            reason = (
                "Follow-up question generated "
                "from a concept missing in "
                "the previous answer."
            )

        elif previous_session_question:

            source_value = (
                previous_session_question.topic
            )

            source_type = "adaptive_followup"

            reason = (
                "Follow-up question generated "
                "from the previous interview topic."
            )

        else:

            source_value = "Machine Learning"

            source_type = "adaptive_followup"

            reason = (
                "Adaptive machine learning "
                "follow-up question."
            )

        # ----------------------------------------------------
        # NEXT SEQUENCE
        # ----------------------------------------------------

        next_sequence = len(attempts) + 1

        # ----------------------------------------------------
        # GENERATE NEXT QUESTION ON DEMAND
        # ----------------------------------------------------

        try:

            generated = generate_question_and_answer(
                source_value=source_value,
                source_type=source_type,
                resume_profile=resume_profile,
                job_profile=job_profile,
                match_result=match_result,
                previous_question=previous_question,
                previous_score=latest_score,
                missing_concepts=missing_concepts
            )

        except Exception as error:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    "Adaptive question generation failed: "
                    f"{str(error)}"
                )
            )

        if not generated:

            raise HTTPException(
                status_code=500,
                detail="No adaptive question was generated"
            )

        # ----------------------------------------------------
        # DUPLICATE QUESTION PROTECTION
        # ----------------------------------------------------

        generated_question = (
            generated.get("question")
        )

        if not generated_question:

            raise HTTPException(
                status_code=500,
                detail="Generated question is empty"
            )

        existing_question = (
            db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.session_id
                == session_id,
                InterviewSessionQuestion.question
                == generated_question
            )
            .first()
        )

        if existing_question:

            # One retry with stronger instruction context
            retry_source = (
                f"{source_value} "
                f"(create a different question)"
            )

            generated = generate_question_and_answer(
                source_value=retry_source,
                source_type=source_type,
                resume_profile=resume_profile,
                job_profile=job_profile,
                match_result=match_result,
                previous_question=previous_question,
                previous_score=latest_score,
                missing_concepts=missing_concepts
            )

            generated_question = (
                generated.get("question")
            )

        if not generated_question:

            raise HTTPException(
                status_code=500,
                detail="Adaptive question generation failed"
            )

        # ----------------------------------------------------
        # SAVE NEW QUESTION
        # ----------------------------------------------------

        new_session_question = InterviewSessionQuestion(
            session_id=session.id,
            question=generated_question,
            category=source_type,
            topic=generated.get(
                "topic",
                source_value
            ),
            difficulty=generated.get(
                "difficulty",
                "Medium"
            ),
            reason=generated.get(
                "reason",
                reason
            ),
            sequence_number=next_sequence,
            ideal_answer=generated.get(
                "ideal_answer"
            ),
            expected_concepts=generated.get(
                "expected_concepts",
                []
            )
        )

        db.add(new_session_question)

        # ----------------------------------------------------
        # UPDATE SESSION
        # ----------------------------------------------------

        session.current_question = next_sequence

        try:

            db.commit()

        except Exception as error:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to save adaptive question: "
                    f"{str(error)}"
                )
            )

        db.refresh(new_session_question)

        # ----------------------------------------------------
        # RETURN NEW QUESTION
        # ----------------------------------------------------

        return {
            "id": new_session_question.id,
            "topic": new_session_question.topic,
            "difficulty": new_session_question.difficulty,
            "question": new_session_question.question
        }

    # ========================================================
    # GENERIC INTERVIEW
    # ========================================================

    attempted_question_ids = get_attempted_question_ids(
        db,
        session_id
    )

    if len(attempted_question_ids) >= session.total_questions:

        session.status = "completed"

        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Interview session is completed"
        )

    if not attempted_question_ids:

        question = (
            db.query(Question)
            .filter(
                Question.topic == session.topic,
                Question.difficulty
                == session.difficulty
            )
            .first()
        )

        if question is None:

            question = (
                db.query(Question)
                .filter(
                    Question.topic == session.topic
                )
                .first()
            )

        if question is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No questions available "
                    "for this topic"
                )
            )

        return question

    latest_attempt = (
        db.query(Attempt)
        .filter(
            Attempt.session_id == session_id
        )
        .order_by(
            Attempt.id.desc()
        )
        .first()
    )

    if latest_attempt is None:

        raise HTTPException(
            status_code=404,
            detail="No previous attempt found"
        )

    latest_evaluation = (
        db.query(Evaluation)
        .filter(
            Evaluation.attempt_id
            == latest_attempt.id
        )
        .first()
    )

    if latest_evaluation is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Evaluation for the previous "
                "answer not found"
            )
        )

    latest_score = latest_evaluation.overall_score

    missing_concepts = (
        latest_evaluation.missing_concepts
        or []
    )

    next_question = select_next_question(
        db=db,
        session=session,
        score=latest_score,
        missing_concepts=missing_concepts
    )

    if next_question is None:

        raise HTTPException(
            status_code=404,
            detail="No more questions available"
        )

    db.commit()
    db.refresh(session)

    return next_question