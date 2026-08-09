import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"


def analyze_repository(files: list) -> str:
    """
    Analyze selected repository files using local Ollama.
    """

    code_context = ""
    files_used = 0

    # Keep the request manageable for the local 1.5B model.
    MAX_FILES = 10
    MAX_FILE_CHARS = 8000

    for file in files[:MAX_FILES]:

        path = file.get("path")
        content = file.get("content", "")

        if not path or not content:
            continue

        # Handle accidental nested content objects.
        if isinstance(content, dict):
            content = content.get("content", "")

        if not isinstance(content, str):
            continue

        content = content[:MAX_FILE_CHARS]

        code_context += (
            f"\n\n===== FILE: {path} =====\n"
            f"{content}\n"
        )

        files_used += 1

    if not code_context:
        raise ValueError(
            "No readable repository files were found."
        )

    prompt = f"""
You are CodeScope AI, a software engineer reviewing a GitHub repository.

Your task is to analyze ONLY the repository files provided below.

IMPORTANT RULES:
- Do not invent files, technologies, features, APIs, or functionality.
- Base every observation on the provided code.
- If something cannot be determined from the provided files, say "Not enough information".
- Mention actual filenames when discussing important components.
- Distinguish existing functionality from suggested improvements.
- Do not write a generic explanation of software development.
- Keep the report concise and useful for a developer or recruiter.

Return the analysis using exactly these sections:

## 1. Project Overview
Briefly explain what the project appears to do.

## 2. Technology Stack
List the technologies that are actually visible in the provided files.

## 3. Architecture
Explain how the major parts of the application interact.

## 4. Important Files
Mention the most important files and explain their roles.

## 5. Code Quality
Mention good practices and any observable weaknesses.

## 6. Potential Issues
Mention specific technical issues or risks visible in the provided code.

## 7. Improvement Suggestions
Give practical improvements based on the observed code.

Files analyzed: {files_used}

Repository files:
{code_context}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 4096,
                },
            },
            timeout=180,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        raise ValueError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running on localhost:11434."
        )

    except requests.exceptions.Timeout:
        raise ValueError(
            "Ollama took too long to respond. "
            "Try analyzing fewer or smaller files."
        )

    except requests.exceptions.RequestException as error:
        raise ValueError(
            f"Ollama request failed: {error}"
        )

    data = response.json()

    result = data.get("response", "")

    if not isinstance(result, str) or not result.strip():
        raise ValueError(
            "Ollama returned an empty response."
        )

    return result.strip()