import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import crud
from app.auth.schemas import SignupIn, LoginIn, TokenOut
from app.auth.security import hash_password
from app.auth.jwt import create_access_token, create_refresh_token

log = logging.getLogger("auth")
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenOut)
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = crud.create_user(db, body.email, hash_password(body.password))
    log.info("user.signup", extra={"user_id": user.id})
    return TokenOut(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )

@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    log.info("user.login", extra={"user_id": user.id})
    return TokenOut(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
