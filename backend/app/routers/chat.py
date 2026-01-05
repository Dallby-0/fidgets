from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.db_models import UserDB
from app.models import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/completion", response_model=ChatResponse)
def chat_completion(
    request: ChatRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """对话推理"""
    chat_service = ChatService()
    try:
        response = chat_service.chat_completion(db, current_user.user_id, request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"推理失败: {str(e)}")

