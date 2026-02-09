import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user_id
from app.db import crud
from app.chat.schemas import CreateConversationOut, ChatIn, ChatOut
from app.chat.graph import run_chat_turn
from app.messaging.kafka import emit

log = logging.getLogger("chat")
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/conversations", response_model=CreateConversationOut)
def create_conversation(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    conv = crud.create_conversation(db, user_id=user_id)
    log.info("chat.conversation.created", extra={"user_id": user_id})
    return CreateConversationOut(conversation_id=conv.id)

@router.post("/conversations/{conversation_id}", response_model=ChatOut)
async def chat_turn(
    conversation_id: int,
    body: ChatIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    conv = crud.get_conversation_for_user(db, user_id=user_id, conversation_id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    crud.add_chat_message(db, conversation_id, "user", body.message)

    response = run_chat_turn(db, user_id, conversation_id, body.message)

    crud.add_chat_message(db, conversation_id, "assistant", response)

    await emit("chat.message.created", {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "type": "turn",
    })

    log.info("chat.turn", extra={"user_id": user_id, "correlation_id": f"conv:{conversation_id}"})
    return ChatOut(response=response)
