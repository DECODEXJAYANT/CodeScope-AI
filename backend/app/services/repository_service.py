from app.services.github_service import get_file_content


def fetch_selected_files(
    owner: str,
    repository: str,
    branch: str,
    selected_files: list,
) -> list:
    """
    Fetch the actual content of selected repository files.

    Returns a list containing:
    - path
    - size
    - content
    - html_url
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

            if not isinstance(file_data, dict):
                print(
                    f"Invalid response while fetching {path}"
                )
                continue

            content = file_data.get("content", "")

            # GitHub service should normally return a string.
            # Do not convert dictionaries/lists into strings.
            if not isinstance(content, str):
                print(
                    f"Skipping {path}: content is not text."
                )
                continue

            if not content.strip():
                print(
                    f"Skipping {path}: file has no readable content."
                )
                continue

            files.append(
                {
                    "path": path,
                    "size": file_data.get(
                        "size",
                        item.get("size", 0),
                    ),
                    "content": content,
                    "html_url": file_data.get(
                        "html_url"
                    ),
                }
            )

        except ValueError as error:
            print(
                f"Could not fetch {path}: {error}"
            )

        except Exception as error:
            print(
                f"Unexpected error while fetching "
                f"{path}: {error}"
            )

    print(
        f"Repository files fetched successfully: "
        f"{len(files)}"
    )

    return files