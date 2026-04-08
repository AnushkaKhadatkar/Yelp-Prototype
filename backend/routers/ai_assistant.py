from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from pymongo.database import Database
from typing import List, Optional

from database import get_db
from services import ai_service

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class RestaurantRecommendation(BaseModel):
    id: int
    name: str
    cuisine: Optional[str] = None
    rating: Optional[float] = None
    avg_rating: Optional[float] = None
    price: Optional[str] = None
    pricing_tier: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    hours: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    recommended_restaurants: List[RestaurantRecommendation] = []


def get_optional_user_id(request: Request):
    """Returns user_id if a valid JWT is present, else None."""
    try:
        import os
        from jose import jwt, JWTError

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")
        secret = os.getenv("SECRET_KEY", "")
        algorithm = os.getenv("ALGORITHM", "HS256")

        payload = jwt.decode(token, secret, algorithms=[algorithm])
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except Exception:
        return None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request_body: ChatRequest,
    request: Request,
    db: Database = Depends(get_db),
):
    try:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in (request_body.conversation_history or [])
        ]

        user_id = get_optional_user_id(request)

        result = await ai_service.chat(
            user_id=user_id,
            message=request_body.message,
            history=history,
            db=db,
        )

        return ChatResponse(
            response=result["response"],
            recommended_restaurants=result.get("recommended_restaurants", []),
        )

    except Exception as e:
        return ChatResponse(
            response=f"I ran into an issue processing your request. Please try again! (Error: {str(e)[:100]})",
            recommended_restaurants=[],
        )
