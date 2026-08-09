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
            file_data = get_file_content(
                owner,
                repository,
                path,
                branch,
            )

            content = file_data.get("content", "")

            if not isinstance(content, str):
                content = str(content)

            files.append(
                {
                    "path": path,
                    "size": file_data.get(
                        "size",
                        item.get("size", 0),
                    ),
                    "content": content,
                    "html_url": file_data.get("html_url"),
                }
            )

        except ValueError as error:
            print(f"Could not fetch {path}: {error}")

    return files