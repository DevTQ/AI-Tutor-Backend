from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.db.base import Base
from app.db.session import engine

# Import all models so SQLAlchemy can register them.
from app import models  # noqa: F401
from app.api.routes_moodle import router as moodle_router
from app.api.routes_learning_profile import router as learning_profile_router
from app.api.routes_recommendation import router as recommendation_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_adaptive_quiz import router as adaptive_quiz_router
from app.api.routes_chatbot import router as chatbot_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import general_exception_handler


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Backend MVP for AI-based Adaptive Learning Tutor integrated with Moodle LMS",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, general_exception_handler)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(moodle_router)
app.include_router(learning_profile_router)
app.include_router(recommendation_router)
app.include_router(analytics_router)
app.include_router(adaptive_quiz_router)
app.include_router(chatbot_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Tutor Backend is running",
    }


@app.get("/health/db")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "not connected",
            "detail": str(e),
        }