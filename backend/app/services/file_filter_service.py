# Directories that should never be analyzed
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
}


# File extensions that usually contain source code
SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".cs",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".vue",
    ".sql",
}


# Important configuration/documentation files
IMPORTANT_FILES = {
    "README.md",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    "pom.xml",
    "build.gradle",
    "Cargo.toml",
    "go.mod",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}


def should_ignore_path(path: str) -> bool:
    """
    Return True if the path belongs to an ignored directory.
    """

    parts = path.replace("\\", "/").split("/")

    return any(
        part in IGNORED_DIRECTORIES
        for part in parts
    )


def is_source_file(path: str) -> bool:
    """
    Check whether a file looks like a source-code file.
    """

    if should_ignore_path(path):
        return False

    filename = path.split("/")[-1]

    if filename in IMPORTANT_FILES:
        return True

    if "." not in filename:
        return False

    extension = "." + filename.rsplit(".", 1)[1].lower()

    return extension in SOURCE_EXTENSIONS


def filter_repository_tree(tree: list) -> list:
    """
    Filter a GitHub repository tree and return
    only relevant files for analysis.
    """

    selected_files = []

    for item in tree:
        if item.get("type") != "blob":
            continue

        path = item.get("path", "")

        if is_source_file(path):
            selected_files.append(item)

    return selected_files