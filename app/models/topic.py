from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="topics")
    learning_resources = relationship("LearningResource", back_populates="topic")
    questions = relationship("Question", back_populates="topic")
    question_attempts = relationship("QuestionAttempt", back_populates="topic")

    __table_args__ = (
        UniqueConstraint("course_id", "name", name="uq_topics_course_id_name"),
    )