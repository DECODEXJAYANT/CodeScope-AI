import json
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"


def analyze_repository(files: list) -> dict:
    """
    Analyze selected repository files using local Ollama.
    """

    code_context = ""
    files_used = 0

    # Keep the input small for the local 1.5B model.
    MAX_FILES = 4
    MAX_FILE_CHARS = 3000

    for file in files[:MAX_FILES]:

        path = file.get("path")
        content = file.get("content", "")

        if not path or not content:
            continue

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

    print("\n========== CODESCOPE AI DEBUG ==========")
    print("Files received:", len(files))
    print("Files sent to Ollama:", files_used)
    print("Context characters:", len(code_context))
    print("========================================\n")

    prompt = f"""
You are CodeScope AI, a software engineer reviewing source code.

Analyze ONLY the files provided below.

Rules:
- Use ONLY evidence from the provided source files.
- Do not use the repository name or general knowledge as evidence.
- Do not assume a technology is used unless it appears in the provided files.
- Do not claim that the entire repository has a feature based on only a few files.
- Do not say that there are "no issues" unless the provided files clearly support that conclusion.
- If something cannot be determined from the provided files, say "Not enough information".
- Clearly distinguish observed functionality from suggested improvements.
- Keep the analysis concise.
- Return ONLY valid JSON.
- Do not use markdown.

Return exactly this structure:

{{
  "project_overview": "Brief description of the project.",
  "technology_stack": [
    {{
      "technology": "Technology name",
      "evidence": "Evidence from the provided files."
    }}
  ],
  "architecture": [
    "Architecture observation."
  ],
  "important_files": [
    {{
      "file": "actual file path",
      "role": "Role of this file."
    }}
  ],
  "code_quality": [
    "Specific code quality observation."
  ],
  "potential_issues": [
    "Specific technical issue."
  ],
  "improvement_suggestions": [
    "Practical improvement."
  ]
}}

Files analyzed: {files_used}

SOURCE CODE:

{code_context}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
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
            "Ollama took too long to respond."
        )

    except requests.exceptions.RequestException as error:
        raise ValueError(
            f"Ollama request failed: {error}"
        )

    data = response.json()

    raw_result = data.get("response", "")

    print("\n========== RAW OLLAMA RESPONSE ==========")
    print(raw_result)
    print("=========================================\n")

    if not isinstance(raw_result, str):
        raise ValueError(
            "Ollama returned an invalid response."
        )

    raw_result = raw_result.strip()

    if not raw_result:
        raise ValueError(
            "Ollama returned an empty response."
        )

    try:
        analysis = json.loads(raw_result)

    except json.JSONDecodeError:
        raise ValueError(
            "Ollama returned invalid JSON."
        )

    if not isinstance(analysis, dict):
        raise ValueError(
            "Ollama returned an unexpected response format."
        )

    # Make sure expected fields exist.
    analysis.setdefault(
        "project_overview",
        "Not enough information"
    )

    analysis.setdefault(
        "technology_stack",
        []
    )

    analysis.setdefault(
        "architecture",
        []
    )

    analysis.setdefault(
        "important_files",
        []
    )

    analysis.setdefault(
        "code_quality",
        []
    )

    analysis.setdefault(
        "potential_issues",
        []
    )

    analysis.setdefault(
        "improvement_suggestions",
        []
    )

    return analysis