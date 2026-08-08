import os

import requests
from dotenv import load_dotenv


load_dotenv()


GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def parse_github_url(repository_url: str):
    """
    Extract owner and repository name from a GitHub URL.
    """

    repository_url = repository_url.strip().rstrip("/")

    if not repository_url.startswith("https://github.com/"):
        raise ValueError("Please provide a valid GitHub repository URL.")

    parts = repository_url.replace(
        "https://github.com/", ""
    ).split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")

    owner = parts[0]
    repository = parts[1].removesuffix(".git")

    if not owner or not repository:
        raise ValueError("Invalid GitHub repository URL.")

    return {
        "owner": owner,
        "repository": repository,
    }


def get_repository_metadata(owner: str, repository: str):
    """
    Fetch repository information from the GitHub API.
    """

    url = f"{GITHUB_API_URL}/repos/{owner}/{repository}"

    headers = {
        "Accept": "application/vnd.github+json",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(
        url,
        headers=headers,
        timeout=10,
        allow_redirects=False,
    )

    # Handle GitHub redirects
    if response.status_code in {301, 302, 307, 308}:
        redirect_url = response.headers.get("Location")

        if not redirect_url:
            raise ValueError(
                "GitHub returned a redirect without a destination."
            )

        response = requests.get(
            redirect_url,
            headers=headers,
            timeout=10,
        )

    if response.status_code == 404:
        raise ValueError("GitHub repository not found.")

    if response.status_code == 403:
        raise ValueError(
            "GitHub API rate limit exceeded or access was denied."
        )

    if response.status_code != 200:
        raise ValueError(
            f"GitHub API returned status {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    # Make sure GitHub returned the repository we requested.
    expected_repository = f"{owner}/{repository}".lower()
    actual_repository = data.get("full_name", "").lower()

    if actual_repository != expected_repository:
        raise ValueError(
            f"GitHub returned '{data.get('full_name')}' "
            f"instead of '{owner}/{repository}'."
        )

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "default_branch": data.get("default_branch"),
        "size": data.get("size"),
        "open_issues": data.get("open_issues_count"),
        "html_url": data.get("html_url"),
    }