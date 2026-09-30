from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Welcome to AI Interview Coach 🚀"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Interview Coach"
    }