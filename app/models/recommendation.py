from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("learning_resources.id"), nullable=True, index=True)

    type = Column(String(50), nullable=False)  # lesson, quiz, review, practice
    title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")  # active, completed, dismissed

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="recommendations")
    course = relationship("Course", back_populates="recommendations")
    resource = relationship("LearningResource", back_populates="recommendations")