from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic Phone Validator"
    API_V1_STR: str = "/api/v1"
    
    # Validation Providers
    NUMVERIFY_API_KEY: Optional[str] = None
    WHAPI_API_TOKEN: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./agent_memory.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
