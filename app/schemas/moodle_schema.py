from typing import List, Optional

from pydantic import BaseModel, Field


class MoodleQuestionAttemptIn(BaseModel):
    question_id: Optional[int] = None
    moodle_question_id: Optional[int] = None

    topic: str = Field(..., examples=["Grammar"])
    difficulty: str = Field(..., examples=["easy"])

    is_correct: bool
    time_spent: Optional[int] = Field(default=None, description="Time spent in seconds")

    content: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None


class MoodleAttemptSyncIn(BaseModel):
    moodle_user_id: int
    fullname: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = "student"

    moodle_course_id: int
    course_name: Optional[str] = None
    course_shortname: Optional[str] = None

    moodle_quiz_id: Optional[int] = None
    moodle_attempt_id: Optional[int] = None

    score: Optional[float] = None
    max_score: Optional[float] = None
    time_spent: Optional[int] = Field(default=None, description="Time spent in seconds")

    questions: List[MoodleQuestionAttemptIn]


class LearningProfileOut(BaseModel):
    user_id: int
    course_id: int
    overall_level: str
    mastery: dict
    weak_topics: list
    strong_topics: list


class MoodleAttemptSyncOut(BaseModel):
    message: str
    quiz_attempt_id: int
    learning_profile: LearningProfileOut