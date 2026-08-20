import json
import requests
from typing import Any

from app.services.evidence_service import (
    extract_repository_evidence,
    extract_package_dependencies,
)


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"

# Ollama is now used only for a compact interpretation step.
OLLAMA_TIMEOUT = 30
OLLAMA_NUM_CTX = 2048


# ============================================================
# FILE PRIORITIES
# ============================================================

PRIORITY_FILES = {
    "readme.md": 100,
    "package.json": 95,
    "requirements.txt": 95,
    "pyproject.toml": 95,
    "dockerfile": 85,
    "docker-compose.yml": 85,
    "docker-compose.yaml": 85,
}


# ============================================================
# PATH HELPERS
# ============================================================

def normalize_path(path: str) -> str:
    """Normalize repository paths."""

    if not isinstance(path, str):
        return ""

    return path.replace("\\", "/").strip()


def get_filename(path: str) -> str:
    """Return lowercase filename."""

    return normalize_path(path).split("/")[-1].lower()


def get_file_priority(path: str) -> int:
    """Assign an analysis priority to a repository file."""

    normalized_path = normalize_path(path)
    filename = get_filename(normalized_path)
    path_lower = normalized_path.lower()

    # Exact path priority
    if path_lower in PRIORITY_FILES:
        return PRIORITY_FILES[path_lower]

    # Important filenames
    if filename in PRIORITY_FILES:
        return PRIORITY_FILES[filename]

    # Configuration files
    if filename in {
        ".env.example",
        "vite.config.js",
        "vite.config.ts",
        "vite.config.jsx",
        "vite.config.tsx",
        "tsconfig.json",
        "next.config.js",
        "next.config.ts",
        "tailwind.config.js",
        "tailwind.config.ts",
    }:
        return 80

    # Backend / service architecture
    if any(
        folder in path_lower
        for folder in [
            "/controllers/",
            "/routes/",
            "/models/",
            "/services/",
            "/middleware/",
            "/config/",
        ]
    ):
        return 70

    # Entry points
    if filename in {
        "main.py",
        "app.py",
        "server.js",
        "server.ts",
        "index.js",
        "index.ts",
        "index.jsx",
        "index.tsx",
        "main.js",
        "main.jsx",
        "main.ts",
        "main.tsx",
        "app.jsx",
        "app.tsx",
        "app.js",
        "app.ts",
    }:
        return 75

    # Frontend architecture
    if any(
        folder in path_lower
        for folder in [
            "/components/",
            "/pages/",
            "/hooks/",
            "/api/",
            "/context/",
            "/router/",
            "/utils/",
        ]
    ):
        return 60

    return 10


# ============================================================
# FILE SELECTION
# ============================================================

def select_files_for_analysis(files: list) -> list:
    """
    Select the most useful repository files for analysis.
    """

    valid_files = []

    for file in files:
        if not isinstance(file, dict):
            continue

        path = file.get("path")
        content = file.get("content", "")

        if not path:
            continue

        if isinstance(content, dict):
            content = content.get("content", "")

        if not isinstance(content, str):
            continue

        if not content.strip():
            continue

        valid_files.append(
            {
                **file,
                "content": content,
                "_priority": get_file_priority(path),
            }
        )

    valid_files.sort(
        key=lambda item: item["_priority"],
        reverse=True,
    )

    return valid_files[:18]


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """Convert arbitrary values into safe text."""

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    try:
        return json.dumps(
            value,
            ensure_ascii=False,
        )
    except Exception:
        return str(value)


def get_file_content(file: dict) -> str:
    """Safely extract file content."""

    if not isinstance(file, dict):
        return ""

    content = file.get("content", "")

    if isinstance(content, dict):
        content = content.get("content", "")

    return normalize_text(content)


def repository_paths(files: list) -> set:
    """Return normalized repository paths."""

    return {
        normalize_path(file.get("path", ""))
        for file in files
        if isinstance(file, dict)
        and file.get("path")
    }


def build_repository_file_list(files: list) -> str:
    """Build a text list of repository files."""

    paths = sorted(repository_paths(files))

    if not paths:
        return "No repository files available."

    return "\n".join(
        f"- {path}"
        for path in paths
    )


# ============================================================
# TECHNOLOGY DETECTION
# ============================================================

TECHNOLOGY_PATTERNS = {
    "React": [
        "from 'react'",
        'from "react"',
        "require('react')",
        'require("react")',
        "react-dom",
        "createRoot(",
        "useState(",
        "useEffect(",
        "useContext(",
    ],

    "React Router DOM": [
        "react-router-dom",
        "BrowserRouter",
        "createBrowserRouter",
        "RouterProvider",
        "useNavigate",
        "useParams",
    ],

    "Vite": [
        "vite.config",
        "@vitejs/plugin-react",
        "@vitejs/plugin-react-swc",
        "from 'vite'",
        'from "vite"',
    ],

    "Tailwind CSS": [
        "tailwindcss",
        "@tailwind",
        "tailwind.config",
    ],

    "Axios": [
        "from 'axios'",
        'from "axios"',
        "require('axios')",
        'require("axios")',
        "axios.",
        "axios(",
    ],

    "Firebase": [
        "firebase/app",
        "firebase/auth",
        "firebase/firestore",
        "firebase/storage",
        "initializeApp(",
    ],

    "Firebase Authentication": [
        "firebase/auth",
        "getAuth(",
        "signInWithEmailAndPassword",
        "createUserWithEmailAndPassword",
        "onAuthStateChanged",
        "sendPasswordResetEmail",
    ],

    "Firestore": [
        "firebase/firestore",
        "getFirestore(",
        "collection(",
        "addDoc(",
        "getDocs(",
        "setDoc(",
        "updateDoc(",
    ],

    "Firebase Storage": [
        "firebase/storage",
        "getStorage(",
        "uploadBytes(",
        "getDownloadURL(",
    ],

    "MongoDB": [
        "mongodb://",
        "mongodb+srv://",
        "mongoose",
    ],

    "Express.js": [
        "express()",
        "require('express')",
        'require("express")',
        "from 'express'",
        'from "express"',
    ],

    "Multer": [
        "multer(",
        "upload.single(",
        "upload.array(",
        "upload.fields(",
    ],

    "JWT": [
        "jsonwebtoken",
        "jwt.sign(",
        "jwt.verify(",
    ],
}


DEPENDENCY_MAPPING = {
    "React": [
        "react",
        "react-dom",
    ],

    "React Router DOM": [
        "react-router-dom",
    ],

    "Vite": [
        "vite",
        "@vitejs/plugin-react",
        "@vitejs/plugin-react-swc",
    ],

    "Tailwind CSS": [
        "tailwindcss",
    ],

    "Axios": [
        "axios",
    ],

    "Firebase": [
        "firebase",
    ],

    "MongoDB": [
        "mongodb",
        "mongoose",
    ],

    "Express.js": [
        "express",
    ],

    "Multer": [
        "multer",
    ],

    "JWT": [
        "jsonwebtoken",
    ],
}


def find_source_evidence_file(
    technology: str,
    repository_files: list,
    dependencies: list,
):
    """
    Find evidence for a technology.

    Source-code evidence is preferred.
    Dependency evidence is only a fallback.
    """

    patterns = TECHNOLOGY_PATTERNS.get(
        technology,
        [],
    )

    # --------------------------------------------------------
    # 1. Search source code
    # --------------------------------------------------------

    for file in repository_files:
        path = normalize_path(
            file.get("path", "")
        )

        content = get_file_content(file)
        content_lower = content.lower()

        for pattern in patterns:
            if pattern.lower() in content_lower:
                return {
                    "file": path,
                    "type": "source",
                    "pattern": pattern,
                }

    # --------------------------------------------------------
    # 2. Search dependency declarations
    # --------------------------------------------------------

    dependency_names = {
        str(item.get("name", "")).lower()
        for item in dependencies
        if isinstance(item, dict)
    }

    package_files = [
        file
        for file in repository_files
        if get_filename(
            file.get("path", "")
        ) == "package.json"
    ]

    for dependency in DEPENDENCY_MAPPING.get(
        technology,
        [],
    ):
        if (
            dependency.lower() in dependency_names
            and package_files
        ):
            return {
                "file": normalize_path(
                    package_files[0].get("path", "")
                ),
                "type": "dependency",
                "pattern": dependency,
            }

    return None


def detect_technologies(
    repository_files: list,
    dependencies: list,
) -> list:

    technologies = []

    for technology in TECHNOLOGY_PATTERNS:
        evidence = find_source_evidence_file(
            technology,
            repository_files,
            dependencies,
        )

        if not evidence:
            continue

        if evidence["type"] == "dependency":
            evidence_text = (
                f"{technology} is declared as a dependency "
                f"in `{evidence['file']}`."
            )

        else:
            evidence_text = (
                f"{technology} is directly referenced in "
                f"`{evidence['file']}`."
            )

            if evidence.get("pattern"):
                evidence_text += (
                    " Evidence includes "
                    f"`{evidence['pattern']}`."
                )

        technologies.append(
            {
                "technology": technology,
                "evidence": evidence_text,
                "source_file": evidence["file"],
                "type": evidence["type"],
            }
        )

    return technologies


# ============================================================
# ARCHITECTURE
# ============================================================

def build_architecture(repository_files: list) -> list:

    paths = [
        normalize_path(
            file.get("path", "")
        )
        for file in repository_files
    ]

    lower_paths = [
        path.lower()
        for path in paths
    ]

    architecture = []

    if any(
        "/pages/" in path
        or path.startswith("src/pages/")
        for path in lower_paths
    ):
        architecture.append(
            "Application pages are organized under a pages directory."
        )

    if any(
        "/components/" in path
        or path.startswith("src/components/")
        for path in lower_paths
    ):
        architecture.append(
            "Reusable UI components are organized under a components directory."
        )

    if any(
        "/hooks/" in path
        or path.startswith("src/hooks/")
        for path in lower_paths
    ):
        architecture.append(
            "Reusable React hooks are organized under a hooks directory."
        )

    if any(
        "/context/" in path
        or path.startswith("src/context/")
        for path in lower_paths
    ):
        architecture.append(
            "Application state/context logic is organized under a context directory."
        )

    if any(
        "/router/" in path
        or path.startswith("src/router/")
        for path in lower_paths
    ):
        architecture.append(
            "Routing logic is organized under a router directory."
        )

    if any(
        "authprovider" in path
        or "/auth/" in path
        for path in lower_paths
    ):
        architecture.append(
            "Authentication-related modules are present in the repository."
        )

    if any(
        "/services/" in path
        or path.startswith("src/services/")
        for path in lower_paths
    ):
        architecture.append(
            "Service-layer logic is organized under a services directory."
        )

    if any(
        "/api/" in path
        or path.startswith("src/api/")
        for path in lower_paths
    ):
        architecture.append(
            "API-related modules are organized under an API directory."
        )

    if any(
        "/utils/" in path
        or path.startswith("src/utils/")
        for path in lower_paths
    ):
        architecture.append(
            "Utility modules are organized under a utils directory."
        )

    all_content = "\n".join(
        get_file_content(file).lower()
        for file in repository_files
    )

    if (
        "firebase/auth" in all_content
        or "firebase/firestore" in all_content
        or "initializeapp(" in all_content
    ):
        architecture.append(
            "Firebase services are integrated into the application."
        )

    if any(
        "tailwind.config" in path
        for path in lower_paths
    ):
        architecture.append(
            "Tailwind CSS configuration is present in the repository."
        )

    if any(
        path.endswith(".py")
        for path in lower_paths
    ):
        architecture.append(
            "Python source files are present in the repository."
        )

    if any(
        path.endswith("server.js")
        or path.endswith("server.ts")
        for path in lower_paths
    ):
        architecture.append(
            "A Node.js server entry point is present in the repository."
        )

    return architecture or [
        "Not enough information"
    ]


# ============================================================
# IMPORTANT FILES
# ============================================================

def build_important_files(
    repository_files: list,
) -> list:

    candidates = []

    for file in repository_files:
        path = normalize_path(
            file.get("path", "")
        )

        if not path:
            continue

        priority = get_file_priority(path)

        if priority < 60:
            continue

        filename = get_filename(path)
        lower_path = path.lower()

        role = None

        if filename == "package.json":
            role = (
                "Project dependency and package configuration."
            )

        elif filename in {
            "vite.config.js",
            "vite.config.ts",
            "vite.config.jsx",
            "vite.config.tsx",
        }:
            role = (
                "Vite build and development configuration."
            )

        elif filename in {
            "tailwind.config.js",
            "tailwind.config.ts",
        }:
            role = (
                "Tailwind CSS configuration."
            )

        elif filename == "readme.md":
            role = "Repository documentation."

        elif filename in {
            "main.jsx",
            "main.tsx",
            "main.js",
            "main.ts",
            "index.jsx",
            "index.tsx",
            "index.js",
            "index.ts",
            "app.jsx",
            "app.tsx",
            "app.js",
            "app.ts",
        }:
            role = (
                "Application entry point or root application module."
            )

        elif "router" in filename:
            role = (
                "Application routing configuration."
            )

        elif "provider" in filename:
            role = (
                "Application state or service provider."
            )

        elif "/context/" in lower_path:
            role = (
                "Application state/context module."
            )

        elif "/hooks/" in lower_path:
            role = (
                "Reusable application hook."
            )

        elif "/pages/" in lower_path:
            role = (
                "Application page/component."
            )

        elif "/utils/" in lower_path:
            role = (
                "Application utility module."
            )

        if role is None:
            continue

        content = get_file_content(file)

        evidence = (
            f"`{path}` exists in the repository."
        )

        if content:

            if "export" in content.lower():
                evidence += (
                    " The file contains exported project code."
                )

            elif "import" in content.lower():
                evidence += (
                    " The file contains project imports."
                )

            else:
                evidence += (
                    " The file contains project source or configuration."
                )

        candidates.append(
            {
                "file": path,
                "role": role,
                "evidence": evidence,
                "_priority": priority,
            }
        )

    candidates.sort(
        key=lambda item: item["_priority"],
        reverse=True,
    )

    candidates = candidates[:10]

    for item in candidates:
        item.pop("_priority", None)

    return candidates or [
        {
            "file": "Not enough information",
            "role": "Not enough information",
            "evidence": "Not enough information",
        }
    ]


# ============================================================
# CODE QUALITY
# ============================================================

def build_code_quality(
    repository_files: list,
) -> list:

    quality = []

    paths = [
        normalize_path(
            file.get("path", "")
        )
        for file in repository_files
    ]

    lower_paths = [
        path.lower()
        for path in paths
    ]

    all_content = "\n".join(
        get_file_content(file)
        for file in repository_files
    )

    all_lower = all_content.lower()

    if any(
        "/hooks/" in path
        or path.startswith("src/hooks/")
        for path in lower_paths
    ):
        quality.append(
            "Reusable hook logic is separated into dedicated files."
        )

    if any(
        "/context/" in path
        or path.startswith("src/context/")
        for path in lower_paths
    ):
        quality.append(
            "Application state/context logic is separated into dedicated files."
        )

    if any(
        "/router/" in path
        or path.startswith("src/router/")
        for path in lower_paths
    ):
        quality.append(
            "Routing configuration is separated into a dedicated module."
        )

    if "usestate(" in all_lower:
        quality.append(
            "The repository uses React state hooks."
        )

    if "useeffect(" in all_lower:
        quality.append(
            "The repository uses React effect hooks."
        )

    if "try {" in all_content or "try:" in all_content:
        quality.append(
            "Error-handling constructs are present in the analyzed source files."
        )

    if any(
        path.endswith(".ts")
        or path.endswith(".tsx")
        for path in lower_paths
    ):
        quality.append(
            "TypeScript source files are present in the repository."
        )

    return quality or [
        "Not enough information"
    ]


# ============================================================
# ISSUE DETECTION
# ============================================================

def detect_issues(
    repository_files: list,
) -> list:

    issues = []

    all_content = "\n".join(
        get_file_content(file)
        for file in repository_files
    )

    all_lower = all_content.lower()

    paths = [
        normalize_path(
            file.get("path", "")
        )
        for file in repository_files
    ]

    # --------------------------------------------------------
    # TODO / FIXME
    # --------------------------------------------------------

    todo_files = []

    for file in repository_files:
        path = normalize_path(
            file.get("path", "")
        )

        content = get_file_content(file)

        if (
            "todo" in content.lower()
            or "fixme" in content.lower()
        ):
            todo_files.append(path)

    if todo_files:
        issues.append(
            "TODO/FIXME markers are present in analyzed "
            "source files: "
            + ", ".join(todo_files[:5])
            + "."
        )

    # --------------------------------------------------------
    # console.log
    # --------------------------------------------------------

    if "console.log(" in all_lower:
        issues.append(
            "console.log statements are present in "
            "the analyzed source files."
        )

    # --------------------------------------------------------
    # Empty catch
    # --------------------------------------------------------

    if (
        "catch (error) {}" in all_lower
        or "catch(error){}" in all_lower
    ):
        issues.append(
            "An empty catch block was detected "
            "in the analyzed source."
        )

    # --------------------------------------------------------
    # localhost
    # --------------------------------------------------------

    if "localhost:" in all_lower:
        issues.append(
            "A localhost URL is present in "
            "the analyzed source files."
        )

    # --------------------------------------------------------
    # TypeScript any
    # --------------------------------------------------------

    if any(
        path.endswith(".ts")
        or path.endswith(".tsx")
        for path in paths
    ):
        if ": any" in all_content:
            issues.append(
                "The analyzed TypeScript source contains "
                "explicit `any` type usage."
            )

    return issues or [
        "Not enough information"
    ]


# ============================================================
# IMPROVEMENTS
# ============================================================

def build_improvements(
    issues: list,
) -> list:

    if (
        not issues
        or issues == ["Not enough information"]
    ):
        return [
            "Not enough information"
        ]

    improvements = []

    for issue in issues:
        lower = issue.lower()

        if "todo/fixme" in lower:
            improvements.append(
                "Review and resolve the TODO/FIXME markers "
                "before considering the affected code complete."
            )

        elif "console.log" in lower:
            improvements.append(
                "Remove or replace development-only console.log "
                "statements with appropriate application logging."
            )

        elif "empty catch" in lower:
            improvements.append(
                "Handle or log the caught error instead of "
                "leaving the catch block empty."
            )

        elif "localhost" in lower:
            improvements.append(
                "Move environment-specific URLs such as "
                "localhost endpoints into environment configuration."
            )

        elif "`any` type usage" in lower:
            improvements.append(
                "Replace unnecessary `any` types with specific "
                "TypeScript types where practical."
            )

    return improvements or [
        "Not enough information"
    ]


# ============================================================
# PROJECT OVERVIEW
# ============================================================

def build_project_overview(
    technologies: list,
    architecture: list,
) -> str:

    technology_names = [
        item["technology"]
        for item in technologies
        if isinstance(item, dict)
        and item.get("technology")
    ]

    if technology_names:
        overview = (
            "The repository contains a "
            + ", ".join(technology_names)
            + " based application."
        )

    else:
        overview = (
            "The repository contains source files "
            "and project configuration."
        )

    real_architecture = [
        item
        for item in architecture
        if item != "Not enough information"
    ]

    if real_architecture:
        overview += " " + " ".join(
            real_architecture[:2]
        )

    return overview


# ============================================================
# OLLAMA COMPACT ANALYSIS
# ============================================================

OLLAMA_SCHEMA = {
    "type": "object",
    "properties": {
        "project_overview": {
            "type": "string"
        },
        "key_findings": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "developer_summary": {
            "type": "string"
        },
    },
    "required": [
        "project_overview",
        "key_findings",
        "developer_summary",
    ],
    "additionalProperties": False,
}


def run_ollama_analysis(
    deterministic_analysis: dict,
    repository_files: list,
    dependencies: list,
) -> dict | None:
    """
    Run Ollama as a compact interpretation layer.

    IMPORTANT:
    Ollama does not receive the raw repository source code.

    It receives only deterministic findings.
    """

    # ========================================================
    # REPOSITORY FILE SUMMARY
    # ========================================================

    paths = sorted(
        repository_paths(repository_files)
    )

    file_summary = "\n".join(
        f"- {path}"
        for path in paths[:18]
    )

    if not file_summary:
        file_summary = (
            "No repository files available."
        )

    # ========================================================
    # DEPENDENCY SUMMARY
    # ========================================================

    dependency_names = []

    for item in dependencies[:40]:
        if not isinstance(item, dict):
            continue

        name = item.get("name")

        if name:
            dependency_names.append(
                str(name)
            )

    dependency_summary = ", ".join(
        dependency_names
    )

    if not dependency_summary:
        dependency_summary = (
            "No dependency information available."
        )

    # ========================================================
    # COMPACT DETERMINISTIC FINDINGS
    # ========================================================

    findings = {
        "project_overview": deterministic_analysis.get(
            "project_overview",
            "Not enough information",
        ),

        "technology_stack": deterministic_analysis.get(
            "technology_stack",
            [],
        ),

        "architecture": deterministic_analysis.get(
            "architecture",
            [],
        ),

        "important_files": deterministic_analysis.get(
            "important_files",
            [],
        ),

        "code_quality": deterministic_analysis.get(
            "code_quality",
            [],
        ),

        "potential_issues": deterministic_analysis.get(
            "potential_issues",
            [],
        ),

        "improvement_suggestions": deterministic_analysis.get(
            "improvement_suggestions",
            [],
        ),
    }

    findings_context = json.dumps(
        findings,
        ensure_ascii=False,
    )

    # Keep the prompt compact.
    findings_context = findings_context[:9000]

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are CodeScope AI.

You are an interpretation layer for a deterministic
repository analysis system.

Do NOT analyze raw source code.

Use ONLY the deterministic findings supplied below.

Do NOT invent facts.

STRICT RULES:

- Never invent technologies.
- Never invent features.
- Never invent databases.
- Never invent APIs.
- Never invent tests.
- Never claim scalability.
- Never claim production readiness.
- Never claim security without direct evidence.
- Do not add facts that are not supported by the findings.
- Keep all output concise.
- If evidence is insufficient, use "Not enough information".

REPOSITORY FILES:

{file_summary}

DECLARED DEPENDENCIES:

{dependency_summary}

DETERMINISTIC FINDINGS:

{findings_context}

Return ONLY valid JSON.

The JSON must have:

- project_overview
- key_findings
- developer_summary
"""

    # ========================================================
    # OLLAMA REQUEST
    # ========================================================

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": OLLAMA_SCHEMA,
                "options": {
                    "temperature": 0,
                    "num_ctx": OLLAMA_NUM_CTX,
                },
            },
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        raw_result = data.get(
            "response",
            "",
        )

        if not isinstance(
            raw_result,
            str,
        ):
            print(
                "Ollama returned a non-string response."
            )

            return None

        raw_result = raw_result.strip()

        if not raw_result:
            print(
                "Ollama returned an empty response."
            )

            return None

        result = json.loads(
            raw_result
        )

        if not isinstance(
            result,
            dict,
        ):
            print(
                "Ollama returned an unexpected response."
            )

            return None

        return result

    except requests.exceptions.ConnectionError:
        print(
            "Ollama unavailable. "
            "Continuing with deterministic analysis."
        )

        return None

    except requests.exceptions.Timeout:
        print(
            "Ollama timed out after "
            f"{OLLAMA_TIMEOUT} seconds. "
            "Continuing with deterministic analysis."
        )

        return None

    except requests.exceptions.HTTPError as error:
        print(
            f"Ollama HTTP error: {error}"
        )

        return None

    except requests.exceptions.RequestException as error:
        print(
            f"Ollama request failed: {error}"
        )

        return None

    except json.JSONDecodeError:
        print(
            "Ollama returned invalid JSON. "
            "Continuing with deterministic analysis."
        )

        return None

    except Exception as error:
        print(
            f"Ollama analysis warning: {error}"
        )

        return None


# ============================================================
# FILE EXPLANATION
# ============================================================

FILE_EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "purpose": {
            "type": "string"
        },
        "summary": {
            "type": "string"
        },
        "imports": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "exports": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "key_points": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "dependencies": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "purpose",
        "summary",
        "imports",
        "exports",
        "key_points",
        "dependencies",
    ],
    "additionalProperties": False,
}


def explain_file(
    file_path: str,
    file_content: str,
) -> dict:
    """
    Explain a single repository file using Qwen.

    Only the supplied file content is sent to Ollama.
    """

    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError(
            "File path is required."
        )

    if not isinstance(file_content, str):
        raise ValueError(
            "File content must be text."
        )

    if not file_content.strip():
        raise ValueError(
            "File has no readable content."
        )

    # Keep file-level prompts bounded.
    max_chars = 12000
    source_code = file_content[:max_chars]

    prompt = f"""
You are CodeScope AI.

Explain the following repository file to a software developer.

FILE PATH:
{file_path}

SOURCE CODE:
{source_code}

STRICT RULES:

- Use ONLY the supplied source code.
- Do not invent functionality.
- Do not invent dependencies.
- Do not invent exports.
- Do not invent APIs.
- Do not claim behavior that is not visible in the code.
- Keep the explanation concise and practical.
- Identify imports visible in the file.
- Identify exports visible in the file.
- Explain the main responsibility of the file.
- Explain important logic, functions, classes, or components.
- If something cannot be determined, use "Not enough information".

Return ONLY valid JSON.

The JSON must contain exactly:

- purpose
- summary
- imports
- exports
- key_points
- dependencies
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": FILE_EXPLANATION_SCHEMA,
                "options": {
                    "temperature": 0,
                    "num_ctx": 4096,
                },
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        raw_result = data.get(
            "response",
            "",
        )

        if not isinstance(raw_result, str):
            raise ValueError(
                "Ollama returned an invalid response."
            )

        raw_result = raw_result.strip()

        if not raw_result:
            raise ValueError(
                "Ollama returned an empty response."
            )

        result = json.loads(raw_result)

        if not isinstance(result, dict):
            raise ValueError(
                "Ollama returned an invalid JSON object."
            )

        return result

    except requests.exceptions.Timeout:
        raise ValueError(
            "File explanation timed out. "
            "Please try again."
        )

    except requests.exceptions.ConnectionError:
        raise ValueError(
            "Ollama is unavailable. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.RequestException as error:
        raise ValueError(
            f"Ollama request failed: {error}"
        )

    except json.JSONDecodeError:
        raise ValueError(
            "Ollama returned invalid JSON."
        )



# ============================================================
# FINAL REPOSITORY ANALYSIS
# ============================================================

def analyze_repository(files: list) -> dict:
    """
    Main CodeScope AI repository analysis pipeline.

    Deterministic analysis is the source of truth.

    Ollama is a supplementary interpretation layer.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not isinstance(files, list):
        raise ValueError(
            "Repository files must be provided as a list."
        )

    selected_files = select_files_for_analysis(
        files
    )

    if not selected_files:
        raise ValueError(
            "No readable repository files were found."
        )

    # --------------------------------------------------------
    # Evidence extraction
    # --------------------------------------------------------

    try:
        evidence = extract_repository_evidence(
            files
        )

    except Exception as error:
        print(
            "Evidence extraction warning:",
            error,
        )

        evidence = {}

    # --------------------------------------------------------
    # Dependency extraction
    # --------------------------------------------------------

    try:
        dependencies = extract_package_dependencies(
            files
        )

    except Exception as error:
        print(
            "Dependency extraction warning:",
            error,
        )

        dependencies = []

    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print(
        "\n========== CODESCOPE AI DEBUG =========="
    )

    print(
        "Files received:",
        len(files),
    )

    print(
        "Files selected:",
        len(selected_files),
    )

    print(
        "Dependencies:",
        len(dependencies),
    )

    print(
        "========================================\n"
    )

    # --------------------------------------------------------
    # Deterministic analysis
    #
    # THIS IS THE SOURCE OF TRUTH.
    # --------------------------------------------------------

    technologies = detect_technologies(
        files,
        dependencies,
    )

    architecture = build_architecture(
        files
    )

    important_files = build_important_files(
        files
    )

    code_quality = build_code_quality(
        files
    )

    potential_issues = detect_issues(
        files
    )

    improvement_suggestions = build_improvements(
        potential_issues
    )

    project_overview = build_project_overview(
        technologies,
        architecture,
    )

    deterministic_analysis = {
        "project_overview": project_overview,
        "technology_stack": technologies,
        "architecture": architecture,
        "important_files": important_files,
        "code_quality": code_quality,
        "potential_issues": potential_issues,
        "improvement_suggestions": improvement_suggestions,
    }

    # --------------------------------------------------------
    # Ollama interpretation
    #
    # Ollama gets ONLY compact deterministic findings.
    # --------------------------------------------------------

    ai_analysis = run_ollama_analysis(
        deterministic_analysis,
        selected_files,
        dependencies,
    )

    if ai_analysis:

        print(
            "\n========== OLLAMA AI INTERPRETATION =========="
        )

        print(
            json.dumps(
                ai_analysis,
                indent=2,
                ensure_ascii=False,
            )
        )

        print(
            "==============================================\n"
        )

    else:

        print(
            "Ollama interpretation unavailable. "
            "Using deterministic repository analysis."
        )

    # --------------------------------------------------------
    # Final result
    #
    # Deterministic result remains authoritative.
    # --------------------------------------------------------

    analysis = deterministic_analysis

    # --------------------------------------------------------
    # Debug output
    # --------------------------------------------------------

    print(
        "\n========== FINAL CODESCOPE ANALYSIS =========="
    )

    print(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(
        "==============================================\n"
    )

    return analysis