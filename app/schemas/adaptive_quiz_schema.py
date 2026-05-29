from typing import Optional

from pydantic import BaseModel, Field


class AdaptiveNextQuestionIn(BaseModel):
    moodle_user_id: int
    moodle_course_id: int

    topic: Optional[str] = Field(default=None, examples=["Grammar"])
    current_difficulty: Optional[str] = Field(default="easy", examples=["easy"])
    last_answer_correct: Optional[bool] = None


class AdaptiveQuestionOut(BaseModel):
    question_id: int
    moodle_question_id: Optional[int] = None

    topic: str
    difficulty: str
    content: str
    explanation: Optional[str] = None

    reason: str