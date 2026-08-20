const API_URL = "http://127.0.0.1:8000";


// ============================================================
// BACKEND HEALTH CHECK
// ============================================================

export async function checkBackend() {
  const response = await fetch(
    `${API_URL}/api/health`
  );

  if (!response.ok) {
    throw new Error(
      "Backend request failed"
    );
  }

  return response.json();
}


// ============================================================
// GET ANALYZABLE REPOSITORY FILES
// ============================================================

export async function getRepositoryFiles(
  repositoryUrl: string
) {
  const response = await fetch(
    `${API_URL}/api/files?repository_url=${encodeURIComponent(
      repositoryUrl
    )}`
  );

  const data = await response.json();

  if (
    !response.ok ||
    data.status !== "success"
  ) {
    throw new Error(
      data.message ||
        "Failed to fetch repository files"
    );
  }

  return data;
}


// ============================================================
// GET SINGLE FILE
// ============================================================

export async function getRepositoryFile(
  repositoryUrl: string,
  filePath: string
) {
  const response = await fetch(
    `${API_URL}/api/file?repository_url=${encodeURIComponent(
      repositoryUrl
    )}&file_path=${encodeURIComponent(
      filePath
    )}`
  );

  const data = await response.json();

  if (
    !response.ok ||
    data.status !== "success"
  ) {
    throw new Error(
      data.message ||
        "Failed to fetch repository file"
    );
  }

  return data;
}


// ============================================================
// AI REPOSITORY ANALYSIS
// ============================================================

export async function analyzeRepository(
  repositoryUrl: string
) {
  const response = await fetch(
    `${API_URL}/api/ai-analyze?repository_url=${encodeURIComponent(
      repositoryUrl
    )}`
  );

  const data = await response.json();

  if (
    !response.ok ||
    data.status !== "success"
  ) {
    throw new Error(
      data.message ||
        "Failed to analyze repository"
    );
  }

  return data;
}


// ============================================================
// DEPENDENCY GRAPH
// ============================================================

export async function getDependencyGraph(
  repositoryUrl: string
) {
  const response = await fetch(
    `${API_URL}/api/dependency-graph?repository_url=${encodeURIComponent(
      repositoryUrl
    )}`
  );

  const data = await response.json();

  if (
    !response.ok ||
    data.status !== "success"
  ) {
    throw new Error(
      data.message ||
        "Failed to generate dependency graph"
    );
  }

  return data;
}

// ============================================================
// EXPLAIN SINGLE REPOSITORY FILE
// ============================================================

export async function explainRepositoryFile(
  repositoryUrl: string,
  filePath: string
) {
  const response = await fetch(
    `${API_URL}/api/explain-file?repository_url=${encodeURIComponent(
      repositoryUrl
    )}&file_path=${encodeURIComponent(
      filePath
    )}`
  );

  const data = await response.json();

  if (
    !response.ok ||
    data.status !== "success"
  ) {
    throw new Error(
      data.message ||
        "Failed to explain repository file"
    );
  }

  return data;
}