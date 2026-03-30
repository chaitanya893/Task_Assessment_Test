from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

# =====================
# CONFIG
# =====================
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "THIS_IS_MY_SUPER_SECRET_KEY_1234567890_CHANGE_IT")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# 🔥 FIX: Swagger must use login-swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-swagger")


# =====================
# GET CURRENT USER
# =====================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return {"user_id": user.id, "email": user.email, "role": user.role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# =====================
# ADMIN ONLY
# =====================
def admin_required(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )
    return user


# =====================
# USER OR ADMIN
# =====================
def user_required(user=Depends(get_current_user)):
    if user["role"] not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    return user