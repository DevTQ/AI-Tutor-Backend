from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)

    content = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False)  # easy, medium, hard
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    source = Column(String(50), nullable=True)  # backend, moodle
    moodle_question_id = Column(Integer, nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    question_attempts = relationship("QuestionAttempt", back_populates="question")