from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)

    moodle_quiz_id = Column(Integer, nullable=True, index=True)
    moodle_attempt_id = Column(Integer, nullable=True, index=True)

    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    time_spent = Column(Integer, nullable=True)  # seconds

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="quiz_attempts")
    course = relationship("Course", back_populates="quiz_attempts")
    question_attempts = relationship("QuestionAttempt", back_populates="quiz_attempt")

    __table_args__ = (
        UniqueConstraint(
            "moodle_attempt_id",
            name="uq_quiz_attempts_moodle_attempt_id",
        ),
    )


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, index=True)

    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)

    difficulty = Column(String(50), nullable=False)  # easy, medium, hard
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, nullable=True)  # seconds

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz_attempt = relationship("QuizAttempt", back_populates="question_attempts")
    question = relationship("Question", back_populates="question_attempts")
    topic = relationship("Topic", back_populates="question_attempts")