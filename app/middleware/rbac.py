from fastapi import HTTPException

def admin_required(user):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")