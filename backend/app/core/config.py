import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Settings(BaseSettings):
    PROJECT_NAME: str = 'Trading Platform'
    API_V1_STR: str = '/api/v1'
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: str

    model_config = ConfigDict(extra='ignore', env_file='.env')

settings = Settings()