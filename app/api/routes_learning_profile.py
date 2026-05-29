from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.course import Course
from app.models.learning_profile import LearningProfile
from app.models.user import User
from app.schemas.moodle_schema import LearningProfileOut
from app.services.learning_profile_service import LearningProfileService
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/learning-profile",
    tags=["Learning Profile"],
)


@router.get("/{moodle_user_id}", response_model=LearningProfileOut)
def get_learning_profile(
    moodle_user_id: int,
    moodle_course_id: int = Query(...),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    user = (
        db.query(User)
        .filter(User.moodle_user_id == moodle_user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    course = (
        db.query(Course)
        .filter(Course.moodle_course_id == moodle_course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    profile = (
        db.query(LearningProfile)
        .filter(
            LearningProfile.user_id == user.id,
            LearningProfile.course_id == course.id,
        )
        .first()
    )

    # Nếu đã có attempt nhưng chưa có profile thì tính lại.
    if not profile:
        profile = LearningProfileService.update_learning_profile(
            db=db,
            user_id=user.id,
            course_id=course.id,
        )

    return {
        "user_id": profile.user_id,
        "course_id": profile.course_id,
        "overall_level": profile.overall_level,
        "mastery": profile.mastery_json,
        "weak_topics": profile.weak_topics_json,
        "strong_topics": profile.strong_topics_json,
    }