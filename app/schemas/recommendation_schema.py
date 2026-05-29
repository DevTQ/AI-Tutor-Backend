from typing import List, Optional

from pydantic import BaseModel


class RecommendationItemOut(BaseModel):
    id: int
    type: str
    title: str
    reason: Optional[str] = None
    status: str
    resource_id: Optional[int] = None
    resource_url: Optional[str] = None
    difficulty: Optional[str] = None
    topic: Optional[str] = None


class RecommendationListOut(BaseModel):
    user_id: int
    course_id: int
    recommendations: List[RecommendationItemOut]