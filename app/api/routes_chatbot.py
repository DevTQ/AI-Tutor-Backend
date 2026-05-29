from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chatbot_schema import ChatbotAskIn, ChatbotAskOut
from app.services.chatbot_service import ChatbotService
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/chatbot",
    tags=["Chatbot"],
)


@router.post("/ask", response_model=ChatbotAskOut)
def ask_chatbot(
    payload: ChatbotAskIn,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    user, course, answer, intent = ChatbotService.ask(
        db=db,
        moodle_user_id=payload.moodle_user_id,
        moodle_course_id=payload.moodle_course_id,
        message=payload.message,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    return {
        "user_id": user.id,
        "course_id": course.id,
        "message": payload.message,
        "answer": answer,
        "intent": intent,
    }