from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation_schema import RecommendationListOut
from app.services.recommendation_service import RecommendationService
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"],
)


@router.get("", response_model=RecommendationListOut)
def get_recommendations(
    moodle_user_id: int = Query(...),
    moodle_course_id: int = Query(...),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    user, course, recommendations = RecommendationService.generate_recommendations(
        db=db,
        moodle_user_id=moodle_user_id,
        moodle_course_id=moodle_course_id,
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
        "recommendations": [
            RecommendationService.format_recommendation(item)
            for item in recommendations
        ],
    }