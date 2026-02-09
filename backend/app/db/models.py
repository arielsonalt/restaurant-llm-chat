from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    category = Column(String(80), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    allergens = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True)

class MenuModifier(Base):
    __tablename__ = "menu_modifiers"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    options_json = Column(Text, nullable=False)  # JSON string for simplicity
    price_delta = Column(Numeric(10, 2), nullable=False, default=0)
    item = relationship("MenuItem")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user/assistant/system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
