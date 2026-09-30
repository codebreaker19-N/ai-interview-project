from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resume import ResumeProfile
from app.models.job_description import JobDescription
from app.services.resume_jd_matcher import match_resume_with_job
from app.utils.auth import get_current_user


router = APIRouter()


@router.get("/resume-jd")
def match_resume_with_jd(
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
        "skills": resume.skills,
        "projects": resume.projects,
        "experience": resume.experience,
        "education": resume.education,
        "achievements": resume.achievements,
        "leadership": resume.leadership,
        "certifications": resume.certifications
    }

    job_profile = {
        "required_skills": job_description.required_skills,
        "preferred_skills": job_description.preferred_skills,
        "responsibilities": job_description.responsibilities,
        "qualifications": job_description.qualifications
    }

    result = match_resume_with_job(
        resume_profile,
        job_profile
    )

    return {
        "resume_id": resume.id,
        "job_description_id": job_description.id,
        "match": result
    }