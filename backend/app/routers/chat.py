import traceback
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat import chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        history = [{"role": m.role, "content": m.content} for m in request.history]
        reply = chat(db, request.message, history)
        return ChatResponse(reply=reply)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Chat error: {tb}")
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": tb})
