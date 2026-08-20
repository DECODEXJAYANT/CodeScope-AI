from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.github_service import (
    parse_github_url,
    get_repository_metadata,
    get_repository_tree,
    get_file_content,
)

from app.services.file_filter_service import filter_repository_tree
from app.services.repository_service import fetch_selected_files
from app.services.ai_service import (
    analyze_repository,
    explain_file,
)
from app.services.dependency_graph_service import build_dependency_graph


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="CodeScope AI API",
    description="Backend API for CodeScope AI",
    version="0.1.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

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


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "message": "CodeScope AI API is running",
    }


# ============================================================
# BASIC REPOSITORY ANALYSIS
# ============================================================

@app.post("/api/analyze")
def analyze_repository_endpoint(repository_url: str):
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


# ============================================================
# GET SINGLE FILE
# ============================================================

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


# ============================================================
# GET ANALYZABLE FILES
# ============================================================

@app.get("/api/files")
def get_analyzable_files(repository_url: str):
    try:
        repository = parse_github_url(repository_url)

        metadata = get_repository_metadata(
            repository["owner"],
            repository["repository"],
        )

        tree_data = get_repository_tree(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
        )

        selected_files = filter_repository_tree(
            tree_data["tree"]
        )

        total_files = len(
            [
                item
                for item in tree_data["tree"]
                if item.get("type") == "blob"
            ]
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "total_files": total_files,
            "selected_files": len(selected_files),
            "files": [
                {
                    "path": item.get("path"),
                    "size": item.get("size"),
                }
                for item in selected_files
            ],
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }


# ============================================================
# FETCH SELECTED REPOSITORY FILES
# ============================================================

@app.get("/api/repository")
def get_repository_files(repository_url: str):
    try:
        repository = parse_github_url(repository_url)

        metadata = get_repository_metadata(
            repository["owner"],
            repository["repository"],
        )

        tree_data = get_repository_tree(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
        )

        selected_files = filter_repository_tree(
            tree_data["tree"]
        )

        files = fetch_selected_files(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
            selected_files,
        )

        total_files = len(
            [
                item
                for item in tree_data["tree"]
                if item.get("type") == "blob"
            ]
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "total_files": total_files,
            "selected_files": len(selected_files),
            "fetched_files": len(files),
            "files": files,
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }


# ============================================================
# AI REPOSITORY ANALYSIS
# ============================================================

@app.get("/api/ai-analyze")
def ai_analyze_repository(repository_url: str):
    try:
        repository = parse_github_url(repository_url)

        metadata = get_repository_metadata(
            repository["owner"],
            repository["repository"],
        )

        tree_data = get_repository_tree(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
        )

        selected_files = filter_repository_tree(
            tree_data["tree"]
        )

        files = fetch_selected_files(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
            selected_files,
        )

        analysis = analyze_repository(files)

        return {
            "status": "success",
            "repository_url": repository_url,
            "analysis": analysis,
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"AI analysis failed: {str(error)}",
        }

# ============================================================
# EXPLAIN SINGLE FILE
# ============================================================

@app.get("/api/explain-file")
def explain_repository_file(
    repository_url: str,
    file_path: str,
):
    try:
        repository = parse_github_url(
            repository_url
        )

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

        explanation = explain_file(
            file_path,
            file_data["content"],
        )

        return {
            "status": "success",
            "repository_url": repository_url,
            "file": file_data,
            "explanation": explanation,
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": (
                f"File explanation failed: {str(error)}"
            ),
        }
    
# ============================================================
# DEPENDENCY GRAPH
# ============================================================

@app.get("/api/dependency-graph")
def dependency_graph(repository_url: str):
    try:
        # --------------------------------------------------------
        # Parse GitHub URL
        # --------------------------------------------------------

        repository = parse_github_url(repository_url)

        # --------------------------------------------------------
        # Get repository metadata
        # --------------------------------------------------------

        metadata = get_repository_metadata(
            repository["owner"],
            repository["repository"],
        )

        # --------------------------------------------------------
        # Get repository tree
        # --------------------------------------------------------

        tree_data = get_repository_tree(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
        )

        # --------------------------------------------------------
        # Filter repository files
        # --------------------------------------------------------

        selected_files = filter_repository_tree(
            tree_data["tree"]
        )

        # --------------------------------------------------------
        # Fetch selected files
        # --------------------------------------------------------

        files = fetch_selected_files(
            repository["owner"],
            repository["repository"],
            metadata["default_branch"],
            selected_files,
        )

        # --------------------------------------------------------
        # Build dependency graph
        # --------------------------------------------------------

        graph = build_dependency_graph(files)

        # --------------------------------------------------------
        # Count total repository files
        # --------------------------------------------------------

        total_files = len(
            [
                item
                for item in tree_data["tree"]
                if item.get("type") == "blob"
            ]
        )

        # --------------------------------------------------------
        # Return dependency graph
        # --------------------------------------------------------

        return {
            "status": "success",
            "repository_url": repository_url,
            "total_files": total_files,
            "analyzed_files": len(files),
            "nodes": graph["nodes"],
            "edges": graph["edges"],
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": (
                f"Dependency graph generation failed: {str(error)}"
            ),
        }