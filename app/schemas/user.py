from pydantic import BaseModel, EmailStr


# -------- REGISTER SCHEMA --------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str   # admin / user


# -------- LOGIN SCHEMA --------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------- RESPONSE SCHEMA --------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True