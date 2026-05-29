from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics_schema import CourseAnalyticsOut, StudentAnalyticsOut
from app.services.analytics_service import AnalyticsService
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get("/student/{moodle_user_id}", response_model=StudentAnalyticsOut)
def get_student_analytics(
    moodle_user_id: int,
    moodle_course_id: int = Query(...),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    user, course, result = AnalyticsService.get_student_analytics(
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

    return result


@router.get("/course/{moodle_course_id}", response_model=CourseAnalyticsOut)
def get_course_analytics(
    moodle_course_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    course, result = AnalyticsService.get_course_analytics(
        db=db,
        moodle_course_id=moodle_course_id,
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    return result