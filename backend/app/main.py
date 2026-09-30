from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.attempts import router as attempts_router

from app.database.database import Base, engine

from app.models.user import User
from app.models.question import Question
from app.models.attempt import Attempt
from app.models.evaluation import Evaluation
from app.models.interview_session import InterviewSession
from app.models.resume import ResumeProfile

from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.questions import router as questions_router
from app.routes.evaluation import router as evaluation_router
from app.routes.interview_session import router as interview_session_router
from app.routes.resume import router as resume_router
from app.routes.job_description import router as job_description_router
from app.routes.matching import router as matching_router
from app.routes.personalized_questions import (
    router as personalized_questions_router
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered technical interview preparation platform",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(
    health_router
)


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)


app.include_router(
    questions_router,
    prefix="/questions",
    tags=["Questions"]
)


app.include_router(
    attempts_router,
    prefix="/interview",
    tags=["Interview"]
)


app.include_router(
    evaluation_router,
    prefix="/evaluation",
    tags=["Evaluation"]
)


app.include_router(
    interview_session_router,
    prefix="/interview",
    tags=["Interview Session"]
)


app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)


app.include_router(
    job_description_router,
    prefix="/job-description",
    tags=["Job Description"]
)


app.include_router(
    matching_router,
    prefix="/matching",
    tags=["Matching"]
)


app.include_router(
    personalized_questions_router,
    prefix="/personalized-questions",
    tags=["Personalized Questions"]
)


app.include_router(
    attempts_router,
    prefix="/attempts",
    tags=["Attempts"]
)