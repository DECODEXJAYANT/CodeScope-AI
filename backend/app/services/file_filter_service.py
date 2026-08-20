# ============================================================
# CodeScope AI - Repository File Filter
# ============================================================
#
# Purpose:
#   Select the most useful repository files for AI analysis.
#
# Strategy:
#   1. Remove files that are unlikely to contain application logic.
#   2. Classify repository files.
#   3. Give each file a deterministic score.
#   4. Guarantee important categories where possible.
#   5. Fill remaining slots using the highest-scoring files.
#   6. Prevent one directory/category from dominating the context.
#
# This service works on GitHub repository tree entries.
# It does NOT fetch file contents.
#
# Expected tree item format:
#
# {
#     "path": "src/App.jsx",
#     "type": "blob",
#     "size": 1234
# }
#
# ============================================================

from __future__ import annotations

import os
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

# Small local model:
# Keep this reasonably small because ai_service.py later
# sends the selected files to Ollama.
MAX_SELECTED_FILES = 18

# Maximum number of files allowed from the same broad category.
MAX_FILES_PER_CATEGORY = 5

# Maximum number of files from the same directory.
MAX_FILES_PER_DIRECTORY = 4


# ============================================================
# FILE EXTENSIONS
# ============================================================

SOURCE_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".java",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".scala",
    ".dart",
    ".vue",
    ".svelte",
}

CONFIG_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
}

STYLE_EXTENSIONS = {
    ".css",
    ".scss",
    ".sass",
    ".less",
}

DOCUMENTATION_FILES = {
    "readme",
    "readme.md",
    "readme.txt",
    "readme.rst",
    "contributing.md",
    "architecture.md",
}

DEPENDENCY_FILES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "pipfile",
    "pipfile.lock",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
}

LOCK_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "uv.lock",
    "poetry.lock",
    "pipfile.lock",
    "cargo.lock",
}

GENERATED_DIRECTORIES = {
    "node_modules",
    ".git",
    ".github",
    ".gitlab",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    ".output",
    ".cache",
    ".vite",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "venv",
    ".venv",
    "env",
    ".env",
    "target",
    "out",
}

ASSET_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".bmp",
    ".tiff",
    ".mp4",
    ".mp3",
    ".wav",
    ".avi",
    ".mov",
    ".webm",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}

TEST_MARKERS = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
    "testing",
}

# ============================================================
# CATEGORY NAMES
# ============================================================

CATEGORY_DOCUMENTATION = "documentation"
CATEGORY_DEPENDENCY = "dependency"
CATEGORY_CONFIGURATION = "configuration"
CATEGORY_ENTRYPOINT = "entrypoint"
CATEGORY_API = "api"
CATEGORY_DATABASE = "database"
CATEGORY_AUTH = "authentication"
CATEGORY_SERVICE = "service"
CATEGORY_CONTROLLER = "controller"
CATEGORY_MODEL = "model"
CATEGORY_CONTEXT = "state"
CATEGORY_PAGE = "page"
CATEGORY_COMPONENT = "component"
CATEGORY_HOOK = "hook"
CATEGORY_MIDDLEWARE = "middleware"
CATEGORY_GENERAL_SOURCE = "source"
CATEGORY_STYLE = "style"


# ============================================================
# HELPERS
# ============================================================

def normalize_path(path: str) -> str:
    """
    Normalize a repository path.
    """

    if not isinstance(path, str):
        return ""

    return path.replace("\\", "/").strip("/")


def filename(path: str) -> str:
    """
    Return lowercase filename.
    """

    normalized = normalize_path(path)

    if not normalized:
        return ""

    return normalized.split("/")[-1].lower()


def filename_without_extension(path: str) -> str:
    """
    Return lowercase filename without extension.
    """

    name = filename(path)

    if not name:
        return ""

    return os.path.splitext(name)[0].lower()


def extension(path: str) -> str:
    """
    Return lowercase extension.
    """

    return os.path.splitext(filename(path))[1].lower()


def path_parts(path: str) -> list[str]:
    """
    Return lowercase path components.
    """

    normalized = normalize_path(path)

    if not normalized:
        return []

    return [
        part.lower()
        for part in normalized.split("/")
        if part
    ]


def directory_of(path: str) -> str:
    """
    Return directory portion of path.
    """

    normalized = normalize_path(path)

    if "/" not in normalized:
        return ""

    return normalized.rsplit("/", 1)[0].lower()


def is_source_file(path: str) -> bool:
    return extension(path) in SOURCE_EXTENSIONS


def is_asset_file(path: str) -> bool:
    return extension(path) in ASSET_EXTENSIONS


def is_lock_file(path: str) -> bool:
    return filename(path) in LOCK_FILES


def is_generated_path(path: str) -> bool:
    parts = path_parts(path)

    return any(
        part in GENERATED_DIRECTORIES
        for part in parts
    )


def is_test_file(path: str) -> bool:
    """
    Detect tests without incorrectly excluding normal source files.
    """

    parts = path_parts(path)

    if any(
        part in TEST_MARKERS
        for part in parts
    ):
        return True

    name = filename_without_extension(path)

    if (
        name.startswith("test_")
        or name.endswith("_test")
        or name.endswith(".test")
        or name.endswith(".spec")
        or name.startswith("spec_")
        or name.endswith("_spec")
    ):
        return True

    return False


# ============================================================
# SPECIAL FILE DETECTION
# ============================================================

def is_readme(path: str) -> bool:
    return filename(path) in DOCUMENTATION_FILES


def is_dependency_file(path: str) -> bool:
    return filename(path) in DEPENDENCY_FILES


def is_config_file(path: str) -> bool:
    name = filename(path)

    if name in {
        "vite.config.js",
        "vite.config.ts",
        "vite.config.jsx",
        "vite.config.tsx",
        "next.config.js",
        "next.config.ts",
        "nuxt.config.js",
        "nuxt.config.ts",
        "webpack.config.js",
        "webpack.config.ts",
        "rollup.config.js",
        "rollup.config.ts",
        "tsconfig.json",
        "jsconfig.json",
        "tailwind.config.js",
        "tailwind.config.ts",
        "tailwind.config.cjs",
        "postcss.config.js",
        "postcss.config.cjs",
        "eslint.config.js",
        "eslint.config.mjs",
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.json",
        "babel.config.js",
        "babel.config.json",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "requirements.txt",
        "pyproject.toml",
    }:
        return True

    return False


# ============================================================
# ENTRY POINT DETECTION
# ============================================================

def is_entrypoint(path: str) -> bool:

    name = filename(path)

    entrypoints = {
        "main.py",
        "app.py",
        "server.py",
        "run.py",
        "wsgi.py",
        "asgi.py",
        "main.js",
        "main.jsx",
        "main.ts",
        "main.tsx",
        "index.js",
        "index.jsx",
        "index.ts",
        "index.tsx",
        "server.js",
        "server.ts",
        "app.js",
        "app.jsx",
        "app.ts",
        "app.tsx",
    }

    if name in entrypoints:
        return True

    return False


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_category(path: str) -> str:

    normalized = normalize_path(path)
    lower = normalized.lower()
    name = filename(path)

    # --------------------------------------------------------
    # Documentation
    # --------------------------------------------------------

    if is_readme(path):
        return CATEGORY_DOCUMENTATION

    # --------------------------------------------------------
    # Dependency
    # --------------------------------------------------------

    if is_dependency_file(path):
        return CATEGORY_DEPENDENCY

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    if is_config_file(path):
        return CATEGORY_CONFIGURATION

    # --------------------------------------------------------
    # Entry point
    # --------------------------------------------------------

    if is_entrypoint(path):
        return CATEGORY_ENTRYPOINT

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    auth_keywords = {
        "auth",
        "authentication",
        "authorize",
        "authorization",
        "login",
        "logout",
        "session",
        "jwt",
        "token",
        "oauth",
        "passport",
    }

    if any(
        keyword in lower
        for keyword in auth_keywords
    ):
        return CATEGORY_AUTH

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    database_keywords = {
        "database",
        "db",
        "models",
        "model",
        "schema",
        "schemas",
        "migration",
        "migrations",
        "repository",
        "repositories",
    }

    if any(
        keyword in lower.split("/")
        for keyword in database_keywords
    ):
        return CATEGORY_DATABASE

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    api_keywords = {
        "api",
        "apis",
        "route",
        "routes",
        "router",
        "routers",
        "endpoint",
        "endpoints",
    }

    if any(
        keyword in lower.split("/")
        for keyword in api_keywords
    ):
        return CATEGORY_API

    # --------------------------------------------------------
    # Middleware
    # --------------------------------------------------------

    if (
        "middleware" in lower
        or name.startswith("middleware")
    ):
        return CATEGORY_MIDDLEWARE

    # --------------------------------------------------------
    # Services
    # --------------------------------------------------------

    service_keywords = {
        "service",
        "services",
        "utils",
        "utility",
        "utilities",
        "lib",
        "libs",
    }

    if any(
        keyword in lower.split("/")
        for keyword in service_keywords
    ):
        return CATEGORY_SERVICE

    # --------------------------------------------------------
    # Controllers
    # --------------------------------------------------------

    if any(
        keyword in lower.split("/")
        for keyword in {
            "controller",
            "controllers",
        }
    ):
        return CATEGORY_CONTROLLER

    # --------------------------------------------------------
    # React state/context
    # --------------------------------------------------------

    if any(
        keyword in lower.split("/")
        for keyword in {
            "context",
            "contexts",
            "store",
            "stores",
            "redux",
            "state",
        }
    ):
        return CATEGORY_CONTEXT

    # --------------------------------------------------------
    # Pages
    # --------------------------------------------------------

    if any(
        keyword in lower.split("/")
        for keyword in {
            "page",
            "pages",
            "screen",
            "screens",
            "views",
            "view",
        }
    ):
        return CATEGORY_PAGE

    # --------------------------------------------------------
    # Hooks
    # --------------------------------------------------------

    if (
        "/hooks/" in lower
        or "/hook/" in lower
        or name.startswith("use")
    ):
        return CATEGORY_HOOK

    # --------------------------------------------------------
    # Components
    # --------------------------------------------------------

    if any(
        keyword in lower.split("/")
        for keyword in {
            "component",
            "components",
            "widget",
            "widgets",
        }
    ):
        return CATEGORY_COMPONENT

    # --------------------------------------------------------
    # Styles
    # --------------------------------------------------------

    if extension(path) in STYLE_EXTENSIONS:
        return CATEGORY_STYLE

    # --------------------------------------------------------
    # General source
    # --------------------------------------------------------

    if is_source_file(path):
        return CATEGORY_GENERAL_SOURCE

    return CATEGORY_GENERAL_SOURCE


# ============================================================
# BASE SCORE
# ============================================================

def calculate_base_score(path: str) -> int:

    normalized = normalize_path(path)
    lower = normalized.lower()
    name = filename(path)

    score = 0

    # --------------------------------------------------------
    # Documentation
    # --------------------------------------------------------

    if is_readme(path):
        score += 100

    # --------------------------------------------------------
    # Dependency files
    # --------------------------------------------------------

    if is_dependency_file(path):
        score += 95

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    if is_config_file(path):
        score += 80

    # --------------------------------------------------------
    # Entry points
    # --------------------------------------------------------

    if is_entrypoint(path):
        score += 90

    # --------------------------------------------------------
    # Backend / API signals
    # --------------------------------------------------------

    if any(
        keyword in lower
        for keyword in [
            "/api/",
            "/routes/",
            "/routers/",
            "/controllers/",
            "/services/",
            "/middleware/",
        ]
    ):
        score += 35

    # --------------------------------------------------------
    # Database signals
    # --------------------------------------------------------

    if any(
        keyword in lower
        for keyword in [
            "/models/",
            "/model/",
            "/database/",
            "/db/",
            "/repositories/",
            "/repository/",
            "/schema/",
            "/schemas/",
            "/migrations/",
        ]
    ):
        score += 35

    # --------------------------------------------------------
    # Authentication signals
    # --------------------------------------------------------

    if any(
        keyword in lower
        for keyword in [
            "auth",
            "authentication",
            "authorization",
            "login",
            "logout",
            "session",
            "jwt",
            "oauth",
        ]
    ):
        score += 30

    # --------------------------------------------------------
    # Frontend application signals
    # --------------------------------------------------------

    if any(
        keyword in lower
        for keyword in [
            "/pages/",
            "/components/",
            "/context/",
            "/hooks/",
            "/store/",
            "/stores/",
        ]
    ):
        score += 20

    # --------------------------------------------------------
    # Source code
    # --------------------------------------------------------

    if is_source_file(path):
        score += 15

    # --------------------------------------------------------
    # Root-level files
    #
    # Root files often describe the application structure.
    # --------------------------------------------------------

    if "/" not in normalized:
        score += 10

    # --------------------------------------------------------
    # Penalize very deeply nested files
    # --------------------------------------------------------

    depth = len(path_parts(path))

    if depth >= 6:
        score -= 10

    if depth >= 8:
        score -= 15

    # --------------------------------------------------------
    # Penalize generated / test / asset files
    # --------------------------------------------------------

    if is_test_file(path):
        score -= 40

    if is_asset_file(path):
        score -= 100

    if is_lock_file(path):
        score -= 50

    if is_generated_path(path):
        score -= 100

    # --------------------------------------------------------
    # Styles are useful, but lower priority than logic.
    # --------------------------------------------------------

    if extension(path) in STYLE_EXTENSIONS:
        score -= 15

    # --------------------------------------------------------
    # Very large source files
    #
    # We still allow them, but they should not dominate selection.
    # --------------------------------------------------------

    return score


# ============================================================
# TREE ITEM SCORE
# ============================================================

def score_tree_item(item: dict[str, Any]) -> dict[str, Any] | None:

    if not isinstance(item, dict):
        return None

    if item.get("type") != "blob":
        return None

    path = normalize_path(
        item.get("path", "")
    )

    if not path:
        return None

    # --------------------------------------------------------
    # Never select obvious generated/assets.
    # --------------------------------------------------------

    if is_generated_path(path):
        return None

    if is_asset_file(path):
        return None

    if is_lock_file(path):
        return None

    # --------------------------------------------------------
    # We generally do not need tests in the main AI context.
    # They can be useful later in a dedicated test analysis.
    # --------------------------------------------------------

    if is_test_file(path):
        return None

    category = detect_category(path)

    score = calculate_base_score(path)

    return {
        "path": path,
        "type": item.get("type"),
        "size": item.get("size", 0),
        "category": category,
        "score": score,
    }


# ============================================================
# CATEGORY PRIORITY
# ============================================================

CATEGORY_PRIORITY = {
    CATEGORY_DOCUMENTATION: 100,
    CATEGORY_DEPENDENCY: 95,
    CATEGORY_ENTRYPOINT: 92,
    CATEGORY_CONFIGURATION: 85,
    CATEGORY_API: 82,
    CATEGORY_DATABASE: 80,
    CATEGORY_AUTH: 78,
    CATEGORY_SERVICE: 75,
    CATEGORY_CONTROLLER: 74,
    CATEGORY_CONTEXT: 68,
    CATEGORY_PAGE: 66,
    CATEGORY_MIDDLEWARE: 64,
    CATEGORY_COMPONENT: 60,
    CATEGORY_HOOK: 58,
    CATEGORY_GENERAL_SOURCE: 50,
    CATEGORY_STYLE: 25,
}


# ============================================================
# CATEGORY GUARANTEES
# ============================================================

# We try to include at least one representative file from
# these categories if such a file exists.
#
# This is important because pure score ranking can accidentally
# select many React components while completely missing the API
# or backend layer.

GUARANTEED_CATEGORIES = [
    CATEGORY_DOCUMENTATION,
    CATEGORY_DEPENDENCY,
    CATEGORY_ENTRYPOINT,
    CATEGORY_CONFIGURATION,
    CATEGORY_API,
    CATEGORY_DATABASE,
    CATEGORY_AUTH,
    CATEGORY_SERVICE,
    CATEGORY_CONTROLLER,
    CATEGORY_CONTEXT,
    CATEGORY_PAGE,
]


# ============================================================
# SORT KEY
# ============================================================

def sort_key(item: dict[str, Any]):

    return (
        item.get("score", 0),
        CATEGORY_PRIORITY.get(
            item.get("category"),
            0,
        ),
        -len(
            path_parts(
                item.get("path", "")
            )
        ),
        -int(
            item.get("size", 0) or 0
        ),
        item.get("path", ""),
    )


# ============================================================
# ADD FILE SAFELY
# ============================================================

def can_add_file(
    item: dict[str, Any],
    selected: list[dict[str, Any]],
    category_counts: dict[str, int],
    directory_counts: dict[str, int],
) -> bool:

    path = item["path"]
    category = item["category"]
    directory = directory_of(path)

    # --------------------------------------------------------
    # Duplicate protection
    # --------------------------------------------------------

    selected_paths = {
        selected_item["path"]
        for selected_item in selected
    }

    if path in selected_paths:
        return False

    # --------------------------------------------------------
    # Category limit
    # --------------------------------------------------------

    current_category_count = (
        category_counts.get(
            category,
            0,
        )
    )

    if (
        current_category_count
        >= MAX_FILES_PER_CATEGORY
    ):
        return False

    # --------------------------------------------------------
    # Directory limit
    # --------------------------------------------------------

    current_directory_count = (
        directory_counts.get(
            directory,
            0,
        )
    )

    if (
        directory
        and current_directory_count
        >= MAX_FILES_PER_DIRECTORY
    ):
        return False

    return True


def add_file(
    item: dict[str, Any],
    selected: list[dict[str, Any]],
    category_counts: dict[str, int],
    directory_counts: dict[str, int],
) -> bool:

    if not can_add_file(
        item,
        selected,
        category_counts,
        directory_counts,
    ):
        return False

    selected.append(item)

    category = item["category"]
    directory = directory_of(
        item["path"]
    )

    category_counts[category] = (
        category_counts.get(
            category,
            0,
        )
        + 1
    )

    if directory:
        directory_counts[directory] = (
            directory_counts.get(
                directory,
                0,
            )
            + 1
        )

    return True


# ============================================================
# SELECT REPRESENTATIVE FILE
# ============================================================

def select_best_from_category(
    category: str,
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    category_counts: dict[str, int],
    directory_counts: dict[str, int],
) -> bool:

    category_candidates = [
        item
        for item in candidates
        if item["category"] == category
    ]

    category_candidates.sort(
        key=sort_key,
        reverse=True,
    )

    for item in category_candidates:

        if add_file(
            item,
            selected,
            category_counts,
            directory_counts,
        ):
            return True

    return False


# ============================================================
# MAIN FILTER
# ============================================================

def filter_repository_tree(
    tree: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Select the most informative repository files.

    Input:
        GitHub repository tree.

    Output:
        Selected tree entries.

    The returned objects preserve the original tree fields
    such as path, type and size.
    """

    if not isinstance(tree, list):
        return []

    # ========================================================
    # STEP 1 - SCORE ALL CANDIDATES
    # ========================================================

    candidates: list[dict[str, Any]] = []

    for item in tree:

        scored = score_tree_item(item)

        if scored is None:
            continue

        candidates.append(scored)

    if not candidates:
        return []

    # ========================================================
    # STEP 2 - SORT
    # ========================================================

    candidates.sort(
        key=sort_key,
        reverse=True,
    )

    # ========================================================
    # STEP 3 - GUARANTEE IMPORTANT CATEGORIES
    # ========================================================

    selected: list[dict[str, Any]] = []

    category_counts: dict[str, int] = {}

    directory_counts: dict[str, int] = {}

    for category in GUARANTEED_CATEGORIES:

        if len(selected) >= MAX_SELECTED_FILES:
            break

        select_best_from_category(
            category,
            candidates,
            selected,
            category_counts,
            directory_counts,
        )

    # ========================================================
    # STEP 4 - FILL REMAINING SLOTS
    # ========================================================

    for item in candidates:

        if len(selected) >= MAX_SELECTED_FILES:
            break

        add_file(
            item,
            selected,
            category_counts,
            directory_counts,
        )

    # ========================================================
    # STEP 5 - FINAL SORT
    #
    # Keep deterministic ordering.
    # ========================================================

    selected.sort(
        key=sort_key,
        reverse=True,
    )

    # ========================================================
    # STEP 6 - REMOVE INTERNAL SCORING FIELDS
    #
    # filter_repository_tree() historically returned GitHub
    # tree objects. Keep that contract.
    # ========================================================

    cleaned: list[dict[str, Any]] = []

    for item in selected:

        cleaned.append(
            {
                key: value
                for key, value in item.items()
                if key not in {
                    "category",
                    "score",
                }
            }
        )

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "\n========== FILE FILTER DEBUG =========="
    )

    print(
        "Repository tree files:",
        len(tree),
    )

    print(
        "Analyzable candidates:",
        len(candidates),
    )

    print(
        "Selected files:",
        len(cleaned),
    )

    for index, item in enumerate(
        cleaned,
        start=1,
    ):

        print(
            f"{index:02d}. {item.get('path')}"
        )

    print(
        "=======================================\n"
    )

    return cleaned