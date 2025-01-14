# fastapi_project/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Project"
    DEBUG: bool = True
    GOOGLE_GENERATIVE_AI_API_KEY: str

    class Config:
        env_file = ".env"  # Đường dẫn tới tệp .env chứa các biến môi trường

settings = Settings()
