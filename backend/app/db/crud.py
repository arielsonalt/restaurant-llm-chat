from sqlalchemy.orm import Session
from app.db import models
from app.auth.security import verify_password

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password_hash: str) -> models.User:
    user = models.User(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_conversation(db: Session, user_id: int) -> models.Conversation:
    conv = models.Conversation(user_id=user_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_conversation_for_user(db: Session, user_id: int, conversation_id: int) -> models.Conversation | None:
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id)
        .first()
    )

def add_chat_message(db: Session, conversation_id: int, role: str, content: str) -> models.ChatMessage:
    msg = models.ChatMessage(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def list_chat_messages(db: Session, conversation_id: int, limit: int = 30):
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.conversation_id == conversation_id)
        .order_by(models.ChatMessage.id.desc())
        .limit(limit)
        .all()[::-1]
    )
