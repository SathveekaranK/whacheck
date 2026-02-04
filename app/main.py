from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import logger

from app.api import endpoints

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from fastapi.staticfiles import StaticFiles

# Include Router
app.include_router(endpoints.router, prefix="/api/v1")

# Mount Static
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}

@app.get("/")
def read_root():
    return {"message": "Agentic Phone Validator API is Running"}

logger.info("Application initialized successfully")
