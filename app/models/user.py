from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class User(Base): 
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    moodle_user_id = Column(Integer, nullable=False, index=True)
    fullname = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    learning_profiles = relationship("LearningProfile", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    chatbot_logs = relationship("ChatbotLog", back_populates="user")

    __table_args__ = (
        UniqueConstraint("moodle_user_id", name="uq_users_moodle_user_id"),
    )