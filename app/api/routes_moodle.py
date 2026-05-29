from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.moodle_schema import MoodleAttemptSyncIn, MoodleAttemptSyncOut
from app.services.moodle_sync_service import MoodleSyncService
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/moodle",
    tags=["Moodle Sync"],
)


@router.post("/sync-attempt", response_model=MoodleAttemptSyncOut)
def sync_attempt(
    payload: MoodleAttemptSyncIn,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    quiz_attempt, profile = MoodleSyncService.sync_attempt(
        db=db,
        payload=payload,
    )

    return {
        "message": "Attempt synced successfully",
        "quiz_attempt_id": quiz_attempt.id,
        "learning_profile": {
            "user_id": profile.user_id,
            "course_id": profile.course_id,
            "overall_level": profile.overall_level,
            "mastery": profile.mastery_json,
            "weak_topics": profile.weak_topics_json,
            "strong_topics": profile.strong_topics_json,
        },
    }