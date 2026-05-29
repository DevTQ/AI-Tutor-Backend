import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "AI Tutor Backend"
    API_VERSION: str = "0.1.0"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "ai_tutor")
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "ai_tutor")

settings = Settings()