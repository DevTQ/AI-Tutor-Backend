from typing import Dict, List, Optional

from pydantic import BaseModel


class StudentAnalyticsOut(BaseModel):
    user_id: int
    course_id: int
    average_score: float
    completion_rate: float
    total_attempts: int
    total_questions: int
    correct_questions: int
    accuracy_rate: float
    overall_level: Optional[str] = None
    topic_mastery: Dict[str, float]
    weak_topics: List[str]
    strong_topics: List[str]


class CourseTopicStatOut(BaseModel):
    topic: str
    total_questions: int
    correct_questions: int
    accuracy_rate: float


class CourseAnalyticsOut(BaseModel):
    course_id: int
    total_students: int
    total_attempts: int
    average_score: float
    low_performance_students: int
    most_failed_topics: List[str]
    topic_stats: List[CourseTopicStatOut]