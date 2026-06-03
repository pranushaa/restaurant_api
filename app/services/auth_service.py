import datetime
import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from app.repositories import user_repo
import mysql.connector
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def register_user(user_name, email, password):
    try:
        hashed_password = pwd_context.hash(password)
        user_repo.db_create_user(user_name, email, hashed_password)
        return {"status": "success", "message": "Registration successful"}
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=400, detail=str(dbrrr))

def login_user(email, password):
    try:
        user = user_repo.db_get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        if not pwd_context.verify(password, user["password"]):
            raise HTTPException(status_code=400, detail="Invalid email or password")
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        token = jwt.encode({"email": user['email'], "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer", "status": "Login Successful!"}
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"Database verification error: {db_err.msg}")