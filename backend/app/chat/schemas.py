from pydantic import BaseModel

class CreateConversationOut(BaseModel):
    conversation_id: int

class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    response: str
