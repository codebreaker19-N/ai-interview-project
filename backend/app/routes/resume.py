import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resume import ResumeProfile
from app.services.resume_parser import parse_resume
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported"
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Resume file is empty"
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        result = parse_resume(temp_path)

        text = result["text"]
        profile = result["profile"]

        existing_resume = (
            db.query(ResumeProfile)
            .filter(ResumeProfile.user_id == user_id)
            .first()
        )

        if existing_resume:
            existing_resume.raw_text = text
            existing_resume.skills = profile.get("skills", [])
            existing_resume.projects = profile.get("projects", [])
            existing_resume.experience = profile.get("experience", [])
            existing_resume.education = profile.get("education", [])
            existing_resume.achievements = profile.get("achievements", [])
            existing_resume.leadership = profile.get("leadership", [])
            existing_resume.certifications = profile.get("certifications", [])

            resume = existing_resume

        else:
            resume = ResumeProfile(
                user_id=user_id,
                raw_text=text,
                skills=profile.get("skills", []),
                projects=profile.get("projects", []),
                experience=profile.get("experience", []),
                education=profile.get("education", []),
                achievements=profile.get("achievements", []),
                leadership=profile.get("leadership", []),
                certifications=profile.get("certifications", [])
            )

            db.add(resume)

        db.commit()
        db.refresh(resume)

        return {
            "message": "Resume uploaded and profile saved successfully",
            "resume_id": resume.id,
            "user_id": user_id,
            "profile": {
                "skills": resume.skills,
                "projects": resume.projects,
                "experience": resume.experience,
                "education": resume.education,
                "achievements": resume.achievements,
                "leadership": resume.leadership,
                "certifications": resume.certifications
            },
            "text_length": len(text)
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(error)}"
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/profile")
def get_resume_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = (
        db.query(ResumeProfile)
        .filter(ResumeProfile.user_id == user_id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume profile not found"
        )

    return {
        "resume_id": resume.id,
        "user_id": resume.user_id,
        "skills": resume.skills
    }