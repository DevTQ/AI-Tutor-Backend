from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # lesson, quiz, video, document
    url = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=True)  # easy, medium, hard
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="learning_resources")
    topic = relationship("Topic", back_populates="learning_resources")
    recommendations = relationship("Recommendation", back_populates="resource")