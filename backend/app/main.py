from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.github_service import (
    parse_github_url,
    get_repository_metadata,
)


app = FastAPI(
    title="CodeScope AI API",
    description="Backend API for CodeScope AI",
    version="0.1.0",
)


# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "message": "CodeScope AI API is running",
    }


@app.post("/api/analyze")
def analyze_repository(repository_url: str):
    try:
        repository = parse_github_url(repository_url)

        metadata = get_repository_metadata(
            repository["owner"],
            repository["repository"],
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "repository": metadata,
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }