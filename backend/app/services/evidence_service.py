import json
from typing import Any


# ============================================================
# PATH / TEXT HELPERS
# ============================================================

def normalize_path(path: str) -> str:
    """Normalize repository paths consistently."""

    if not isinstance(path, str):
        return ""

    return path.replace("\\", "/").strip()


def normalize_text(value: Any) -> str:
    """Convert arbitrary values into searchable text."""

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


def get_filename(path: str) -> str:
    """Return lowercase filename from repository path."""

    path = normalize_path(path)

    if not path:
        return ""

    return path.split("/")[-1].lower()


def file_matches(
    source_file: str,
    repository_files: list,
) -> list:
    """
    Find repository files referenced by the AI.

    Supports:
        README.md
        package.json
        src/App.jsx
        backend/server.js

    Also supports filename-only responses:
        App.jsx

    when actual repository path is:
        src/App.jsx
    """

    if not isinstance(source_file, str):
        return []

    source_file = normalize_path(source_file)

    if not source_file:
        return []

    requested_paths = [
        item.strip()
        for item in source_file.split(",")
        if item.strip()
    ]

    matches = []

    for requested in requested_paths:

        requested = normalize_path(requested)

        if not requested:
            continue

        requested_lower = requested.lower()

        for repo_file in repository_files:

            if not isinstance(repo_file, dict):
                continue

            path = normalize_path(
                repo_file.get("path", "")
            )

            if not path:
                continue

            path_lower = path.lower()

            # Exact path
            if path_lower == requested_lower:

                if repo_file not in matches:
                    matches.append(repo_file)

                continue

            # Filename fallback
            if (
                get_filename(path)
                == get_filename(requested)
            ):

                if repo_file not in matches:
                    matches.append(repo_file)

    return matches


def search_in_file(
    repository_file: dict,
    terms: list[str],
) -> bool:
    """Return True if at least one term exists in a file."""

    if not isinstance(repository_file, dict):
        return False

    content = normalize_text(
        repository_file.get(
            "content",
            "",
        )
    )

    if not content:
        return False

    content_lower = content.lower()

    for term in terms:

        if not isinstance(term, str):
            continue

        if not term:
            continue

        if term.lower() in content_lower:
            return True

    return False


def get_repository_file(
    repository_files: list,
    requested_path: str,
):
    """Return first repository file matching requested path."""

    matches = file_matches(
        requested_path,
        repository_files,
    )

    if matches:
        return matches[0]

    return None


# ============================================================
# TECHNOLOGY DEFINITIONS
# ============================================================

TECHNOLOGY_PATTERNS = {

    "React": [
        "from 'react'",
        'from "react"',
        "require('react')",
        'require("react")',
        "react-dom",
        "useState(",
        "useEffect(",
        "useContext(",
        "createContext(",
        "ReactDOM",
    ],

    "React Router DOM": [
        "react-router-dom",
        "BrowserRouter",
        "Routes",
        "Route",
        "useNavigate(",
        "useParams(",
    ],

    "Vite": [
        "vite.config",
        "@vitejs/plugin-react",
        "@vitejs/plugin-react-swc",
        "from 'vite'",
        'from "vite"',
        '"vite":',
        "'vite':",
    ],

    "Tailwind CSS": [
        "tailwindcss",
        "tailwind.config",
        "@tailwind",
        "className=",
        "className={`",
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
        "initializeApp(",
    ],

    "Firebase Authentication": [
        "firebase/auth",
        "getAuth(",
        "signInWithEmailAndPassword(",
        "createUserWithEmailAndPassword(",
        "onAuthStateChanged(",
    ],

    "Firestore": [
        "firebase/firestore",
        "getFirestore(",
        "collection(",
        "addDoc(",
        "getDocs(",
        "setDoc(",
        "updateDoc(",
        "deleteDoc(",
    ],

    "MongoDB": [
        "mongodb://",
        "mongodb+srv://",
        "mongoose.connect(",
        "mongoose.model(",
        "mongoose.Schema(",
        "mongoose.schema(",
    ],

    "Express.js": [
        "from 'express'",
        'from "express"',
        "require('express')",
        'require("express")',
        "express()",
        "express.Router(",
        "app.get(",
        "app.post(",
        "app.put(",
        "app.patch(",
        "app.delete(",
    ],

    "Node.js": [
        "node:",
        "process.version",
        "process.argv",
        "module.exports",
    ],

    "Multer": [
        "require('multer')",
        'require("multer")',
        "from 'multer'",
        'from "multer"',
        "multer(",
        "upload.single(",
        "upload.array(",
        "upload.fields(",
    ],

    "JWT": [
        "jsonwebtoken",
        "jwt.sign(",
        "jwt.verify(",
        "jwt.decode(",
    ],

    "Python": [
    "import os",
    "import sys",
    "import json",
    "from os ",
    "from sys ",
    "from json ",
    "def ",
    "if __name__ ==",
    "print(",
    ],
}


# ============================================================
# TECHNOLOGY ALIASES
# ============================================================

TECHNOLOGY_ALIASES = {

    "react.js": "React",
    "reactjs": "React",
    "react": "React",

    "react router": "React Router DOM",
    "react-router": "React Router DOM",
    "react-router-dom": "React Router DOM",

    "vite": "Vite",

    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",

    "axios": "Axios",

    "firebase": "Firebase",

    "firebase auth": "Firebase Authentication",
    "firebase authentication": "Firebase Authentication",

    "firestore": "Firestore",
    "cloud firestore": "Firestore",

    "mongo": "MongoDB",
    "mongodb": "MongoDB",

    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",

    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",

    "multer": "Multer",

    "jwt": "JWT",
    "json web token": "JWT",
    "json web tokens": "JWT",

    "python": "Python",
}


def normalize_technology_name(
    technology: str,
) -> str:
    """Convert AI technology names into canonical names."""

    if not isinstance(
        technology,
        str,
    ):
        return ""

    cleaned = technology.strip().lower()

    return TECHNOLOGY_ALIASES.get(
        cleaned,
        technology.strip(),
    )


# ============================================================
# PACKAGE -> TECHNOLOGY MAPPING
# ============================================================

PACKAGE_TECHNOLOGY_MAP = {

    "react": "React",
    "react-dom": "React",

    "react-router-dom": "React Router DOM",

    "vite": "Vite",
    "@vitejs/plugin-react": "Vite",
    "@vitejs/plugin-react-swc": "Vite",

    "tailwindcss": "Tailwind CSS",

    "axios": "Axios",

    "firebase": "Firebase",

    "mongoose": "MongoDB",
    "mongodb": "MongoDB",

    "express": "Express.js",

    "multer": "Multer",

    "jsonwebtoken": "JWT",
}


# ============================================================
# DEPENDENCY EXTRACTION
# ============================================================

def extract_package_dependencies(
    repository_files: list,
) -> list[dict]:
    """
    Extract dependencies from package.json.

    IMPORTANT:
    Empty package.json files are ignored safely.
    """

    dependencies = []

    for file in repository_files:

        if not isinstance(file, dict):
            continue

        path = normalize_path(
            file.get("path", "")
        )

        if get_filename(path) != "package.json":
            continue

        content = file.get(
            "content",
            "",
        )

        if isinstance(content, dict):

            content = content.get(
                "content",
                "",
            )

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        try:

            package_data = json.loads(
                content
            )

        except Exception:

            continue

        if not isinstance(
            package_data,
            dict,
        ):
            continue

        for section in [
            "dependencies",
            "devDependencies",
        ]:

            packages = package_data.get(
                section,
                {},
            )

            if not isinstance(
                packages,
                dict,
            ):
                continue

            for package_name, version in packages.items():

                dependencies.append(
                    {
                        "name": package_name,
                        "version": str(version),
                        "source_file": path,
                        "section": section,
                    }
                )

    return dependencies


# ============================================================
# TECHNOLOGY EVIDENCE EXTRACTION
# ============================================================

def extract_technology_evidence(
    repository_files: list,
) -> dict:
    """
    Build trusted technology evidence.

    Evidence levels:

    1. Source usage
    2. package.json dependency
    3. README mention
    """

    evidence = {}

    dependencies = extract_package_dependencies(
        repository_files
    )

    # --------------------------------------------------------
    # 1. PACKAGE DEPENDENCY EVIDENCE
    # --------------------------------------------------------

    for dependency in dependencies:

        package_name = dependency[
            "name"
        ].lower()

        technology = PACKAGE_TECHNOLOGY_MAP.get(
            package_name
        )

        if not technology:
            continue

        if technology not in evidence:

            evidence[technology] = {
                "technology": technology,
                "evidence": [],
                "source_files": [],
                "usage_confirmed": False,
                "dependency_confirmed": False,
                "readme_only": False,
            }

        evidence[
            technology
        ][
            "dependency_confirmed"
        ] = True

        evidence[
            technology
        ][
            "evidence"
        ].append(
            (
                f"{dependency['name']} "
                f"{dependency['version']} is declared in "
                f"{dependency['source_file']}."
            )
        )

        if (
            dependency["source_file"]
            not in evidence[
                technology
            ]["source_files"]
        ):

            evidence[
                technology
            ]["source_files"].append(
                dependency["source_file"]
            )

    # --------------------------------------------------------
    # 2. SOURCE CODE EVIDENCE
    # --------------------------------------------------------

    for file in repository_files:

        if not isinstance(file, dict):
            continue

        path = normalize_path(
            file.get("path", "")
        )

        if not path:
            continue

        if get_filename(path) == "readme.md":
            continue

        content = normalize_text(
            file.get(
                "content",
                "",
            )
        )

        if not content:
            continue

        content_lower = content.lower()

        for technology, patterns in (
            TECHNOLOGY_PATTERNS.items()
        ):

            found_pattern = None

            for pattern in patterns:

                if (
                    pattern.lower()
                    in content_lower
                ):

                    found_pattern = pattern
                    break

            if not found_pattern:
                continue

            if technology not in evidence:

                evidence[technology] = {
                    "technology": technology,
                    "evidence": [],
                    "source_files": [],
                    "usage_confirmed": False,
                    "dependency_confirmed": False,
                    "readme_only": False,
                }

            evidence[
                technology
            ]["usage_confirmed"] = True

            evidence[
                technology
            ]["readme_only"] = False

            evidence[
                technology
            ]["evidence"].append(
                (
                    f"Pattern '{found_pattern}' "
                    f"was found in {path}."
                )
            )

            if (
                path
                not in evidence[
                    technology
                ]["source_files"]
            ):

                evidence[
                    technology
                ]["source_files"].append(
                    path
                )

    # --------------------------------------------------------
    # 3. README EVIDENCE
    # --------------------------------------------------------

    for readme in repository_files:

        if not isinstance(readme, dict):
            continue

        readme_path = normalize_path(
            readme.get(
                "path",
                "",
            )
        )

        if get_filename(readme_path) != "readme.md":
            continue

        readme_content = normalize_text(
            readme.get(
                "content",
                "",
            )
        ).lower()

        if not readme_content:
            continue

        for technology, patterns in (
            TECHNOLOGY_PATTERNS.items()
        ):

            if technology in evidence:
                continue

            for pattern in patterns:

                if (
                    pattern.lower()
                    in readme_content
                ):

                    evidence[technology] = {
                        "technology": technology,
                        "evidence": [
                            (
                                f"{readme_path} mentions "
                                f"{technology}."
                            )
                        ],
                        "source_files": [
                            readme_path
                        ],
                        "usage_confirmed": False,
                        "dependency_confirmed": False,
                        "readme_only": True,
                    }

                    break

    return evidence


# ============================================================
# TECHNOLOGY CLAIM VALIDATION
# ============================================================

def validate_technology_claim(
    claim: dict,
    repository_files: list,
) -> bool:
    """
    Validate AI technology claim against actual repository.

    IMPORTANT:
    If AI gives a wrong source path, we DO NOT automatically
    trust the AI path.

    We check the repository evidence instead.
    """

    if not isinstance(
        claim,
        dict,
    ):
        return False

    raw_technology = claim.get(
        "technology",
        "",
    )

    if not isinstance(
        raw_technology,
        str,
    ):
        return False

    technology = normalize_technology_name(
        raw_technology
    )

    if not technology:
        return False

    evidence = extract_technology_evidence(
        repository_files
    )

    trusted = evidence.get(
        technology
    )

    if not trusted:
        return False

    # --------------------------------------------------------
    # If AI supplied a source path, check it.
    # --------------------------------------------------------

    source_file = claim.get(
        "source_file",
        "",
    )

    if not isinstance(
        source_file,
        str,
    ):
        source_file = ""

    source_file = source_file.strip()

    if source_file:

        matched_files = file_matches(
            source_file,
            repository_files,
        )

        if matched_files:

            patterns = TECHNOLOGY_PATTERNS.get(
                technology,
                [],
            )

            for repo_file in matched_files:

                path = normalize_path(
                    repo_file.get(
                        "path",
                        "",
                    )
                )

                content = normalize_text(
                    repo_file.get(
                        "content",
                        "",
                    )
                ).lower()

                if (
                    get_filename(path)
                    == "readme.md"
                ):
                    continue

                for pattern in patterns:

                    if (
                        pattern.lower()
                        in content
                    ):

                        return True

            # package.json dependency validation
            for repo_file in matched_files:

                path = normalize_path(
                    repo_file.get(
                        "path",
                        "",
                    )
                )

                if (
                    get_filename(path)
                    != "package.json"
                ):
                    continue

                package_content = normalize_text(
                    repo_file.get(
                        "content",
                        "",
                    )
                )

                try:

                    package_data = json.loads(
                        package_content
                    )

                except Exception:

                    continue

                for section in [
                    "dependencies",
                    "devDependencies",
                ]:

                    packages = package_data.get(
                        section,
                        {},
                    )

                    if not isinstance(
                        packages,
                        dict,
                    ):
                        continue

                    for package_name in packages:

                        mapped = (
                            PACKAGE_TECHNOLOGY_MAP.get(
                                package_name.lower()
                            )
                        )

                        if mapped == technology:
                            return True

        # ----------------------------------------------------
        # IMPORTANT:
        # Wrong AI source path should NOT delete a technology
        # if the repository independently proves that technology.
        # ----------------------------------------------------

        if (
            trusted.get("usage_confirmed")
            or trusted.get("dependency_confirmed")
        ):

            return True

        # README-only evidence is weaker.
        if trusted.get("readme_only"):
            return True

        return False

    # --------------------------------------------------------
    # No AI source path.
    # Trusted repository evidence is enough.
    # --------------------------------------------------------

    return True


# ============================================================
# SANITIZE TECHNOLOGY STACK
# ============================================================

def sanitize_technology_stack(
    technology_stack: list,
    repository_files: list,
) -> list:
    """
    Remove unsupported technologies.

    If AI gives a wrong source path but the repository
    proves the technology elsewhere, recover the real
    repository evidence/source path.
    """

    if not isinstance(
        technology_stack,
        list,
    ):
        return []

    sanitized = []

    seen = set()

    trusted_evidence = extract_technology_evidence(
        repository_files
    )

    for claim in technology_stack:

        if not isinstance(
            claim,
            dict,
        ):
            continue

        raw_name = claim.get(
            "technology",
            "",
        )

        technology = normalize_technology_name(
            raw_name
        )

        if not technology:
            continue

        key = technology.lower()

        if key in seen:
            continue

        if not validate_technology_claim(
            claim,
            repository_files,
        ):

            print(
                "REMOVED UNSUPPORTED TECHNOLOGY:",
                raw_name,
                claim.get(
                    "source_file",
                    "",
                ),
            )

            continue

        trusted = trusted_evidence.get(
            technology
        )

        if not trusted:
            continue

        # ----------------------------------------------------
        # ALWAYS use trusted repository source files.
        # Never trust hallucinated AI paths.
        # ----------------------------------------------------

        actual_sources = trusted.get(
            "source_files",
            [],
        )

        actual_sources = [
            normalize_path(path)
            for path in actual_sources
            if normalize_path(path)
        ]

        if not actual_sources:
            continue

        # ----------------------------------------------------
        # Build trusted evidence wording.
        # ----------------------------------------------------

        usage_confirmed = trusted.get(
            "usage_confirmed",
            False,
        )

        dependency_confirmed = trusted.get(
            "dependency_confirmed",
            False,
        )

        readme_only = trusted.get(
            "readme_only",
            False,
        )

        if usage_confirmed:

            evidence_text = (
                f"{technology} usage was detected in "
                f"{', '.join(actual_sources)}."
            )

        elif dependency_confirmed:

            evidence_text = (
                f"{technology} is declared as a dependency "
                f"in {', '.join(actual_sources)}."
            )

        elif readme_only:

            evidence_text = (
                f"{technology} is mentioned in "
                f"{', '.join(actual_sources)}."
            )

        else:

            evidence_text = (
                "Supported by repository evidence."
            )

        seen.add(key)

        sanitized.append(
            {
                "technology": technology,
                "evidence": evidence_text,
                "source_file": ", ".join(
                    actual_sources
                ),
            }
        )

    return sanitized


# ============================================================
# ARCHITECTURE VALIDATION
# ============================================================

def validate_architecture_claim(
    claim: Any,
    repository_files: list,
) -> bool:
    """
    Validate architecture statement.

    Generic AI praise is rejected.

    A claim must contain a concrete technical concept
    that actually appears in repository files.
    """

    if not isinstance(
        claim,
        str,
    ):
        return False

    claim_lower = claim.lower().strip()

    if not claim_lower:
        return False

    if claim_lower == "not enough information":
        return True

    forbidden_phrases = [
        "follows best practices",
        "scalable microservice architecture",
        "highly scalable",
        "secure architecture",
        "modern architecture",
        "efficient architecture",
        "production-ready",
        "well structured",
        "well-organized",
        "well organized",
        "easy maintenance",
        "easy to maintain",
        "best practice",
        "clear separation of concerns",
    ]

    for phrase in forbidden_phrases:

        if phrase in claim_lower:
            return False

    evidence_terms = [
        "react",
        "vite",
        "express",
        "mongodb",
        "mongoose",
        "firebase",
        "firestore",
        "axios",
        "router",
        "redux",
        "context",
        "api",
        "route",
        "database",
        "frontend",
        "backend",
        "component",
        "middleware",
        "authentication",
        "cart",
        "state",
        "hook",
    ]

    matched_terms = [
        term
        for term in evidence_terms
        if term in claim_lower
    ]

    if not matched_terms:
        return False

    for term in matched_terms:

        for repo_file in repository_files:

            if search_in_file(
                repo_file,
                [term],
            ):

                return True

    return False


def sanitize_architecture(
    architecture: list,
    repository_files: list,
) -> list:
    """Remove unsupported architecture claims."""

    if not isinstance(
        architecture,
        list,
    ):
        return [
            "Not enough information"
        ]

    sanitized = []

    seen = set()

    for claim in architecture:

        if not isinstance(
            claim,
            str,
        ):
            continue

        cleaned = claim.strip()

        if not cleaned:
            continue

        if not validate_architecture_claim(
            cleaned,
            repository_files,
        ):

            print(
                "REMOVED UNSUPPORTED ARCHITECTURE:",
                cleaned,
            )

            continue

        key = cleaned.lower()

        if key in seen:
            continue

        seen.add(key)

        sanitized.append(
            cleaned
        )

    if not sanitized:

        return [
            "Not enough information"
        ]

    return sanitized


# ============================================================
# IMPORTANT FILE VALIDATION
# ============================================================

def sanitize_important_files(
    important_files: list,
    repository_files: list,
) -> list:
    """
    Keep only files that actually exist in repository.

    AI paths are never trusted blindly.
    """

    if not isinstance(
        important_files,
        list,
    ):
        return []

    sanitized = []

    seen = set()

    for item in important_files:

        if not isinstance(
            item,
            dict,
        ):
            continue

        requested_file = item.get(
            "file",
            "",
        )

        if not isinstance(
            requested_file,
            str,
        ):
            continue

        requested_file = requested_file.strip()

        if not requested_file:
            continue

        matches = file_matches(
            requested_file,
            repository_files,
        )

        if not matches:

            print(
                "REMOVED UNKNOWN IMPORTANT FILE:",
                requested_file,
            )

            continue

        repo_file = matches[0]

        actual_path = normalize_path(
            repo_file.get(
                "path",
                "",
            )
        )

        if not actual_path:
            continue

        key = actual_path.lower()

        if key in seen:
            continue

        seen.add(key)

        role = item.get(
            "role",
            "Not enough information",
        )

        evidence = item.get(
            "evidence",
            "Repository file exists.",
        )

        if not isinstance(role, str):
            role = "Not enough information"

        if not isinstance(evidence, str):
            evidence = "Repository file exists."

        sanitized.append(
            {
                "file": actual_path,
                "role": role.strip()
                or "Not enough information",
                "evidence": evidence.strip()
                or "Repository file exists.",
            }
        )

    return sanitized


# ============================================================
# CODE QUALITY VALIDATION
# ============================================================

def sanitize_code_quality(
    code_quality: list,
    repository_files: list,
) -> list:
    """
    Remove unsupported generic quality claims.
    """

    if not isinstance(
        code_quality,
        list,
    ):
        return [
            "Not enough information"
        ]

    sanitized = []

    generic_phrases = [
        "well structured",
        "well-organized",
        "well organized",
        "follows best practices",
        "best practices",
        "high quality",
        "clean and readable",
        "easy to understand",
        "maintainable",
        "scalable",
        "reliable",
        "secure",
        "no significant issues",
        "no significant problems",
    ]

    observable_terms = [
        "hook",
        "useeffect",
        "usestate",
        "usecontext",
        "function",
        "component",
        "import",
        "export",
        "try",
        "except",
        "catch",
        "validation",
        "error",
        "duplicate",
        "hard-coded",
        "hardcoded",
        "unused",
        "test",
        "eslint",
        "async",
        "await",
        "context",
        "props",
    ]

    for claim in code_quality:

        if not isinstance(
            claim,
            str,
        ):
            continue

        cleaned = claim.strip()

        if not cleaned:
            continue

        claim_lower = cleaned.lower()

        is_generic = any(
            phrase in claim_lower
            for phrase in generic_phrases
        )

        if is_generic:

            concrete = False

            for term in observable_terms:

                if term not in claim_lower:
                    continue

                for repo_file in repository_files:

                    if search_in_file(
                        repo_file,
                        [term],
                    ):

                        concrete = True
                        break

                if concrete:
                    break

            if not concrete:

                print(
                    "REMOVED UNSUPPORTED CODE QUALITY:",
                    cleaned,
                )

                continue

        if (
            "no significant issue"
            in claim_lower
            or "no significant problem"
            in claim_lower
        ):

            print(
                "REMOVED UNSUPPORTED CODE QUALITY:",
                cleaned,
            )

            continue

        sanitized.append(cleaned)

    if not sanitized:

        return [
            "Not enough information"
        ]

    return sanitized


# ============================================================
# ISSUE VALIDATION
# ============================================================

def sanitize_potential_issues(
    issues: list,
) -> list:
    """
    Remove fake/no-issue claims and generic statements.
    """

    if not isinstance(
        issues,
        list,
    ):
        return [
            "Not enough information"
        ]

    sanitized = []

    forbidden = [
        "there are no bugs",
        "no known issues",
        "no potential issues",
        "no issues",
        "bug free",
        "bug-free",
        "fully secure",
        "well-maintained",
        "well maintained",
        "no problems",
        "no known security vulnerabilities",
        "no security vulnerabilities",
        "project is secure",
        "application is secure",
    ]

    issue_terms = [
        "missing",
        "hard-coded",
        "hardcoded",
        "error",
        "validation",
        "duplicate",
        "unused",
        "security",
        "exception",
        "failed",
        "does not",
        "not handled",
        "without",
        "incorrect",
        "inconsistent",
        "deprecated",
        "vulnerability",
        "risk",
        "bug",
        "problem",
    ]

    for issue in issues:

        if not isinstance(
            issue,
            str,
        ):
            continue

        cleaned = issue.strip()

        if not cleaned:
            continue

        lowered = cleaned.lower()

        if lowered == "not enough information":

            sanitized.append(
                "Not enough information"
            )

            continue

        if any(
            phrase in lowered
            for phrase in forbidden
        ):

            print(
                "REMOVED UNSUPPORTED ISSUE:",
                cleaned,
            )

            continue

        if not any(
            term in lowered
            for term in issue_terms
        ):

            print(
                "REMOVED GENERIC ISSUE:",
                cleaned,
            )

            continue

        sanitized.append(
            cleaned
        )

    if not sanitized:

        return [
            "Not enough information"
        ]

    return sanitized


# ============================================================
# IMPROVEMENT VALIDATION
# ============================================================

def sanitize_improvement_suggestions(
    suggestions: list,
    issues: list,
) -> list:
    """
    Keep improvement suggestions only when actual
    potential issues were detected.
    """

    if not isinstance(
        suggestions,
        list,
    ):
        return [
            "Not enough information"
        ]

    if not isinstance(
        issues,
        list,
    ):
        issues = []

    real_issues = [
        issue
        for issue in issues
        if isinstance(issue, str)
        and issue.strip().lower()
        != "not enough information"
    ]

    if not real_issues:

        return [
            "Not enough information"
        ]

    sanitized = []

    for suggestion in suggestions:

        if not isinstance(
            suggestion,
            str,
        ):
            continue

        cleaned = suggestion.strip()

        if not cleaned:
            continue

        if (
            cleaned.lower()
            == "not enough information"
        ):
            continue

        sanitized.append(
            cleaned
        )

    if not sanitized:

        return [
            "Not enough information"
        ]

    return sanitized


# ============================================================
# PROJECT OVERVIEW
# ============================================================

def sanitize_project_overview(
    overview: Any,
) -> str:
    """Ensure project overview is always a usable string."""

    if not isinstance(
        overview,
        str,
    ):
        return "Not enough information"

    overview = overview.strip()

    if not overview:
        return "Not enough information"

    return overview


# ============================================================
# FINAL ANALYSIS SANITIZATION
# ============================================================

def sanitize_analysis(
    analysis: dict,
    repository_files: list,
) -> dict:
    """
    Final deterministic evidence firewall.
    """

    if not isinstance(
        analysis,
        dict,
    ):

        return {
            "project_overview": (
                "Not enough information"
            ),
            "technology_stack": [],
            "architecture": [
                "Not enough information"
            ],
            "important_files": [],
            "code_quality": [
                "Not enough information"
            ],
            "potential_issues": [
                "Not enough information"
            ],
            "improvement_suggestions": [
                "Not enough information"
            ],
        }

    # --------------------------------------------------------
    # Project overview
    # --------------------------------------------------------

    analysis["project_overview"] = (
        sanitize_project_overview(
            analysis.get(
                "project_overview",
                "",
            )
        )
    )

    # --------------------------------------------------------
    # Technology
    # --------------------------------------------------------

    analysis["technology_stack"] = (
        sanitize_technology_stack(
            analysis.get(
                "technology_stack",
                [],
            ),
            repository_files,
        )
    )

    # --------------------------------------------------------
    # Architecture
    # --------------------------------------------------------

    analysis["architecture"] = (
        sanitize_architecture(
            analysis.get(
                "architecture",
                [],
            ),
            repository_files,
        )
    )

    # --------------------------------------------------------
    # Important files
    # --------------------------------------------------------

    analysis["important_files"] = (
        sanitize_important_files(
            analysis.get(
                "important_files",
                [],
            ),
            repository_files,
        )
    )

    # --------------------------------------------------------
    # Code quality
    # --------------------------------------------------------

    analysis["code_quality"] = (
        sanitize_code_quality(
            analysis.get(
                "code_quality",
                [],
            ),
            repository_files,
        )
    )

    # --------------------------------------------------------
    # Potential issues
    # --------------------------------------------------------

    analysis["potential_issues"] = (
        sanitize_potential_issues(
            analysis.get(
                "potential_issues",
                [],
            )
        )
    )

    # --------------------------------------------------------
    # Improvements
    # --------------------------------------------------------

    analysis["improvement_suggestions"] = (
        sanitize_improvement_suggestions(
            analysis.get(
                "improvement_suggestions",
                [],
            ),
            analysis.get(
                "potential_issues",
                [],
            ),
        )
    )

    return analysis


# ============================================================
# MAIN EVIDENCE EXTRACTION
# ============================================================

def extract_repository_evidence(
    repository_files: list,
) -> dict:
    """Main evidence extraction entry point."""

    technology_evidence = (
        extract_technology_evidence(
            repository_files
        )
    )

    dependencies = (
        extract_package_dependencies(
            repository_files
        )
    )

    return {
        "technologies": technology_evidence,
        "dependencies": dependencies,
    }