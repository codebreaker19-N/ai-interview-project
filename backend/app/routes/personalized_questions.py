from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resume import ResumeProfile
from app.models.job_description import JobDescription
from app.services.personalized_question_generator import (
    generate_personalized_questions
)
from app.utils.auth import get_current_user


router = APIRouter()


@router.get("/generate")
def generate_questions(
    resume_id: int,
    job_description_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = (
        db.query(ResumeProfile)
        .filter(
            ResumeProfile.id == resume_id,
            ResumeProfile.user_id == user_id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    job_description = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_description_id,
            JobDescription.user_id == user_id
        )
        .first()
    )

    if not job_description:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    resume_profile = {
        "skills": resume.skills or [],
        "projects": resume.projects or [],
        "experience": resume.experience or [],
        "education": resume.education or [],
        "achievements": resume.achievements or [],
        "leadership": resume.leadership or [],
        "certifications": resume.certifications or []
    }

    job_profile = {
        "required_skills": (
            job_description.required_skills or []
        ),
        "preferred_skills": (
            job_description.preferred_skills or []
        ),
        "responsibilities": (
            job_description.responsibilities or []
        ),
        "qualifications": (
            job_description.qualifications or []
        )
    }

    try:
        result = generate_personalized_questions(
            resume_profile=resume_profile,
            job_profile=job_profile
        )

        return {
            "resume_id": resume.id,
            "job_description_id": job_description.id,
            "questions": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Personalized question generation failed: "
                f"{str(error)}"
            )
        )