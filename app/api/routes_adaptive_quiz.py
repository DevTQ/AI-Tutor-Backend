from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.adaptive_quiz_schema import AdaptiveNextQuestionIn, AdaptiveQuestionOut
from app.services.adaptive_quiz_service import AdaptiveQuizService
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/adaptive-quiz",
    tags=["Adaptive Quiz"],
)


@router.post("/next-question", response_model=AdaptiveQuestionOut)
def get_next_question(
    payload: AdaptiveNextQuestionIn,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    user, course, question, reason = AdaptiveQuizService.get_next_question(
        db=db,
        moodle_user_id=payload.moodle_user_id,
        moodle_course_id=payload.moodle_course_id,
        topic=payload.topic,
        current_difficulty=payload.current_difficulty,
        last_answer_correct=payload.last_answer_correct,
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

    if not question:
        raise HTTPException(
            status_code=404,
            detail="No suitable question found",
        )

    return {
        "question_id": question.id,
        "moodle_question_id": question.moodle_question_id,
        "topic": question.topic.name if question.topic else "",
        "difficulty": question.difficulty,
        "content": question.content,
        "explanation": question.explanation,
        "reason": reason,
    }