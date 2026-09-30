from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.job_description import JobDescription
from app.services.job_description_parser import parse_job_description
from app.utils.auth import get_current_user


router = APIRouter()


# ============================================================
# SCHEMA
# ============================================================

class JobDescriptionCreate(BaseModel):
    job_description: str


# ============================================================
# UPLOAD / PARSE JOB DESCRIPTION
# ============================================================

@router.post("/upload")
def upload_job_description(
    data: JobDescriptionCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not data.job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    try:

        # ----------------------------------------------------
        # PARSE JOB DESCRIPTION
        # ----------------------------------------------------

        result = parse_job_description(
            data.job_description
        )

        text = result["text"]
        profile = result["profile"]

        # ----------------------------------------------------
        # CREATE DATABASE RECORD
        # ----------------------------------------------------

        job_description = JobDescription(
            user_id=user_id,

            raw_text=text,

            required_skills=profile.get(
                "required_skills",
                []
            ),

            preferred_skills=profile.get(
                "preferred_skills",
                []
            ),

            responsibilities=profile.get(
                "responsibilities",
                []
            ),

            qualifications=profile.get(
                "qualifications",
                []
            )
        )

        db.add(job_description)

        db.commit()

        db.refresh(job_description)

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "message":
                "Job description parsed and saved successfully",

            "job_description_id":
                job_description.id,

            "user_id":
                user_id,

            "profile": {

                "required_skills":
                    job_description.required_skills,

                "preferred_skills":
                    job_description.preferred_skills,

                "responsibilities":
                    job_description.responsibilities,

                "qualifications":
                    job_description.qualifications
            }
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Job description processing failed: "
                f"{str(error)}"
            )
        )


# ============================================================
# GET ALL JOB DESCRIPTIONS FOR CURRENT USER
# ============================================================

@router.get("")
def get_job_descriptions(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    job_descriptions = (
        db.query(JobDescription)
        .filter(
            JobDescription.user_id == user_id
        )
        .order_by(
            JobDescription.id.desc()
        )
        .all()
    )

    return [
        {
            "id": job.id,

            "raw_text":
                job.raw_text,

            "required_skills":
                job.required_skills,

            "preferred_skills":
                job.preferred_skills,

            "responsibilities":
                job.responsibilities,

            "qualifications":
                job.qualifications
        }

        for job in job_descriptions
    ]


# ============================================================
# GET SINGLE JOB DESCRIPTION
# ============================================================

@router.get("/{job_description_id}")
def get_job_description(
    job_description_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

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

    return {
        "id":
            job_description.id,

        "user_id":
            job_description.user_id,

        "raw_text":
            job_description.raw_text,

        "required_skills":
            job_description.required_skills,

        "preferred_skills":
            job_description.preferred_skills,

        "responsibilities":
            job_description.responsibilities,

        "qualifications":
            job_description.qualifications
    }