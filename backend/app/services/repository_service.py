from app.services.github_service import get_file_content


def fetch_selected_files(
    owner: str,
    repository: str,
    branch: str,
    selected_files: list,
) -> list:
    """
    Fetch the actual content of selected repository files.
    """

    files = []

    for item in selected_files:
        path = item.get("path")

        if not path:
            continue

        try:
            content = get_file_content(
                owner,
                repository,
                path,
                branch,
            )

            files.append(
                {
                    "path": path,
                    "size": item.get("size", 0),
                    "content": content,
                }
            )

        except ValueError as error:
            print(
                f"Could not fetch {path}: {error}"
            )

    return files