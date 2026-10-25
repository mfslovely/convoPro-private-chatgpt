from dotenv import load_dotenv

from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MONGODB_DB_URL: str
    MONGODB_DB_NAME: str
    OLLAMA_URL: str
    OLLAMA_MODELS: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
