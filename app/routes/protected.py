from fastapi import APIRouter, Depends
from app.utils.jwt_handler import get_current_user

router = APIRouter()


@router.get("/protected")
def protected(user=Depends(get_current_user)):
    return {
        "message": "OK",
        "user": user
    }