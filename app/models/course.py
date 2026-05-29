from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    moodle_course_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    shortname = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    topics = relationship("Topic", back_populates="course")
    learning_resources = relationship("LearningResource", back_populates="course")
    questions = relationship("Question", back_populates="course")
    quiz_attempts = relationship("QuizAttempt", back_populates="course")
    learning_profiles = relationship("LearningProfile", back_populates="course")
    recommendations = relationship("Recommendation", back_populates="course")
    chatbot_logs = relationship("ChatbotLog", back_populates="course")

    __table_args__ = (
        UniqueConstraint("moodle_course_id", name="uq_courses_moodle_course_id"),
    )