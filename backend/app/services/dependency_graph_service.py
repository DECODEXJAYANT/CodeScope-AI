import re
from typing import Any


# ============================================================
# SOURCE FILE CONFIGURATION
# ============================================================

SOURCE_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


# ============================================================
# PATH HELPERS
# ============================================================

def normalize_path(path: str) -> str:
    """Normalize repository paths and resolve . / .. segments."""

    if not isinstance(path, str):
        return ""

    path = path.replace("\\", "/")

    while "//" in path:
        path = path.replace("//", "/")

    parts: list[str] = []

    for part in path.split("/"):
        if not part or part == ".":
            continue

        if part == "..":
            if parts:
                parts.pop()
            continue

        parts.append(part)

    return "/".join(parts)


def get_extension(path: str) -> str:
    """Return the lowercase file extension."""

    normalized = normalize_path(path)

    filename = normalized.split("/")[-1]

    if "." not in filename:
        return ""

    return "." + filename.rsplit(".", 1)[-1].lower()


def is_source_file(path: str) -> bool:
    """Return True when the path is a supported source file."""

    return get_extension(path) in SOURCE_EXTENSIONS


def get_file_content(file: dict[str, Any]) -> str:
    """Safely extract source file content."""

    if not isinstance(file, dict):
        return ""

    content = file.get("content", "")

    if isinstance(content, dict):
        content = content.get("content", "")

    if not isinstance(content, str):
        return ""

    return content


# ============================================================
# FILE CATEGORY
# ============================================================

def get_file_category(path: str) -> str:
    """
    Categorize a source file for frontend visualization.

    Examples:

        pages/Home.jsx          -> page
        components/Navbar.jsx   -> component
        hooks/useAuth.jsx       -> hook
        context/Cart.jsx        -> context
        router/Router.jsx       -> router
        utils/helper.js         -> utility
        config.js               -> config
        other.js                -> source
    """

    normalized = normalize_path(path)
    lower_path = normalized.lower()

    filename = normalized.split("/")[-1].lower()

    if "/pages/" in lower_path:
        return "page"

    if "/components/" in lower_path:
        return "component"

    if "/hooks/" in lower_path:
        return "hook"

    if "/context/" in lower_path:
        return "context"

    if "/router/" in lower_path:
        return "router"

    if "/utils/" in lower_path:
        return "utility"

    if (
        filename.startswith("config")
        or filename.endswith(".config.js")
        or filename.endswith(".config.ts")
    ):
        return "config"

    return "source"


# ============================================================
# JAVASCRIPT / TYPESCRIPT IMPORT EXTRACTION
# ============================================================

IMPORT_PATTERNS = [
    # import Something from "./Something"
    re.compile(
        r"""import\s+(?:[\s\S]*?\s+from\s+)?["']([^"']+)["']""",
        re.MULTILINE,
    ),

    # export { something } from "./Something"
    re.compile(
        r"""export\s+(?:[\s\S]*?\s+from\s+)["']([^"']+)["']""",
        re.MULTILINE,
    ),

    # require("./Something")
    re.compile(
        r"""require\s*\(\s*["']([^"']+)["']\s*\)""",
        re.MULTILINE,
    ),

    # dynamic import("./Something")
    re.compile(
        r"""import\s*\(\s*["']([^"']+)["']\s*\)""",
        re.MULTILINE,
    ),
]


def extract_import_paths(content: str) -> list[str]:
    """
    Extract literal JavaScript/TypeScript import paths.
    """

    if not isinstance(content, str) or not content.strip():
        return []

    imports: set[str] = set()

    for pattern in IMPORT_PATTERNS:
        matches = pattern.findall(content)

        for match in matches:
            if isinstance(match, str) and match.strip():
                imports.add(match.strip())

    return sorted(imports)


# ============================================================
# RELATIVE IMPORT RESOLUTION
# ============================================================

def resolve_relative_import(
    source_file: str,
    import_path: str,
    repository_paths: set[str],
) -> str | None:
    """
    Resolve a relative JavaScript/TypeScript import
    to an actual repository file.

    Supported examples:

        ./Home
        ../context/CartProvider
        ./components/Button
        ./router/Router.jsx
    """

    if not import_path:
        return None

    # Ignore external packages.
    #
    # Examples:
    #
    # react
    # axios
    # firebase
    # react-router-dom
    #
    if not (
        import_path.startswith("./")
        or import_path.startswith("../")
    ):
        return None

    source_path = normalize_path(source_file)

    if "/" in source_path:
        source_directory = source_path.rsplit("/", 1)[0]
    else:
        source_directory = ""

    if source_directory:
        combined_path = (
            f"{source_directory}/{import_path}"
        )
    else:
        combined_path = import_path

    combined_path = normalize_path(combined_path)

    # Normalize repository paths once.
    normalized_repository_paths = {
        normalize_path(path)
        for path in repository_paths
    }

    # --------------------------------------------------------
    # Candidate resolution
    # --------------------------------------------------------

    candidates: list[str] = []

    # Exact path.
    candidates.append(combined_path)

    # File extensions.
    for extension in sorted(SOURCE_EXTENSIONS):
        candidates.append(
            combined_path + extension
        )

    # Index files.
    for extension in sorted(SOURCE_EXTENSIONS):
        candidates.append(
            f"{combined_path}/index{extension}"
        )

    # --------------------------------------------------------
    # Find actual repository file.
    # --------------------------------------------------------

    for candidate in candidates:
        candidate = normalize_path(candidate)

        if candidate in normalized_repository_paths:
            return candidate

    return None


# ============================================================
# DEPENDENCY EXTRACTION FOR ONE FILE
# ============================================================

def extract_file_dependencies(
    file: dict[str, Any],
    repository_paths: set[str],
) -> list[dict[str, str]]:
    """
    Extract local dependency edges from one source file.
    """

    if not isinstance(file, dict):
        return []

    source = normalize_path(
        file.get("path", "")
    )

    if not source:
        return []

    if not is_source_file(source):
        return []

    content = get_file_content(file)

    if not content:
        return []

    import_paths = extract_import_paths(content)

    dependencies: list[dict[str, str]] = []

    for import_path in import_paths:

        target = resolve_relative_import(
            source,
            import_path,
            repository_paths,
        )

        if not target:
            continue

        dependencies.append(
            {
                "source": source,
                "target": target,
                "import": import_path,
            }
        )

    return dependencies


# ============================================================
# GRAPH BUILDER
# ============================================================

def build_dependency_graph(
    repository_files: list,
) -> dict:
    """
    Build a repository dependency graph.

    Nodes:
        Source files.

    Edges:
        Local file -> imported local file.
    """

    if not isinstance(repository_files, list):
        return {
            "nodes": [],
            "edges": [],
        }

    # --------------------------------------------------------
    # Repository paths
    # --------------------------------------------------------

    repository_paths: set[str] = set()

    for file in repository_files:

        if not isinstance(file, dict):
            continue

        path = normalize_path(
            file.get("path", "")
        )

        if path:
            repository_paths.add(path)

    # --------------------------------------------------------
    # Source paths
    # --------------------------------------------------------

    source_paths = sorted(
        path
        for path in repository_paths
        if is_source_file(path)
    )

    # --------------------------------------------------------
    # Build nodes
    # --------------------------------------------------------

    nodes: list[dict[str, Any]] = []

    for path in source_paths:

        nodes.append(
            {
                "id": path,
                "type": "file",
                "label": path.split("/")[-1],
                "category": get_file_category(path),
                "path": path,
            }
        )

    # --------------------------------------------------------
    # Build edges
    # --------------------------------------------------------

    edges: list[dict[str, str]] = []

    seen_edges: set[tuple[str, str]] = set()

    for file in repository_files:

        if not isinstance(file, dict):
            continue

        dependencies = extract_file_dependencies(
            file,
            repository_paths,
        )

        for dependency in dependencies:

            source = dependency["source"]
            target = dependency["target"]

            edge_key = (
                source,
                target,
            )

            # Prevent duplicate edges.
            if edge_key in seen_edges:
                continue

            seen_edges.add(edge_key)

            edges.append(
                {
                    "source": source,
                    "target": target,
                    "import": dependency["import"],
                }
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    connected_nodes: set[str] = set()

    for edge in edges:
        connected_nodes.add(edge["source"])
        connected_nodes.add(edge["target"])

    # --------------------------------------------------------
    # Final graph
    # --------------------------------------------------------

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_source_files": len(source_paths),
            "connected_files": len(connected_nodes),
            "dependency_count": len(edges),
        },
    }

