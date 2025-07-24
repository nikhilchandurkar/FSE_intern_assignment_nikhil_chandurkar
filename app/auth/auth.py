# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from jose import jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from app.db.database import get_db
# from app.db import models
# import os

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")

# router = APIRouter()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def create_token(data: dict):
#     to_encode = data.copy()
#     to_encode.update({"exp": datetime.utcnow() + timedelta(hours=1)})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# @router.post("/signup")
# async def signup(email: str, password: str, name: str, role: str, db: AsyncSession = Depends(get_db)):
#     user = models.User(email=email, password=pwd_context.hash(password), name=name, role=role)
#     db.add(user)
#     await db.commit()
#     return {"message": "User created"}

# @router.post("/login")
# async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(models.User.__table__.select().where(models.User.email == email))
#     user = result.fetchone()
#     if not user or not pwd_context.verify(password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid")
#     token = create_token({"sub": user.email, "role": user.role})
#     return {"access_token": token}















from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.db.models import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.hash import verify_password, get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

auth_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@auth_router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully"}

@auth_router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
        "sub": db_user.email,
        "role": db_user.role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}