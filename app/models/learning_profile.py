from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)

    overall_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced

    mastery_json = Column(JSONB, nullable=False, default=dict)
    weak_topics_json = Column(JSONB, nullable=False, default=list)
    strong_topics_json = Column(JSONB, nullable=False, default=list)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="learning_profiles")
    course = relationship("Course", back_populates="learning_profiles")

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_learning_profiles_user_course"),
    )