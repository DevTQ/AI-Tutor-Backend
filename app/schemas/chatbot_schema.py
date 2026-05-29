from typing import Optional

from pydantic import BaseModel


class ChatbotAskIn(BaseModel):
    moodle_user_id: int
    moodle_course_id: int
    message: str


class ChatbotAskOut(BaseModel):
    user_id: int
    course_id: int
    message: str
    answer: str
    intent: Optional[str] = None