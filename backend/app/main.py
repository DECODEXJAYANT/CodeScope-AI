from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.github_service import (
    parse_github_url,
    get_repository_metadata,
    get_repository_tree,
    get_file_content,
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

        tree = get_repository_tree(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "repository": metadata,
            "tree": tree["tree"],
            "tree_truncated": tree["truncated"],
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }

@app.get("/api/file")
def get_file(
    repository_url: str,
    file_path: str,
):
    try:
        repository = parse_github_url(repository_url)

        metadata = get_repository_metadata(
            repository["owner"],
            repository["repository"],
        )

        file_data = get_file_content(
            repository["owner"],
            repository["repository"],
            file_path,
            metadata["default_branch"],
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "file": file_data,
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }    