# 🚀 CodeScope AI

### AI-Powered Codebase Understanding & Dependency Analysis Platform

CodeScope AI is a developer-focused platform that analyzes public GitHub repositories and helps developers understand unfamiliar codebases faster.

It combines repository analysis, architecture detection, dependency visualization, source-code exploration, and AI-powered file explanations in a single platform.

---

## 📌 Overview

Understanding an unfamiliar repository can take a significant amount of time.

Developers often need to:

- Explore hundreds or thousands of files
- Identify the technology stack
- Understand the project architecture
- Trace dependencies between modules
- Open individual files and understand their purpose

CodeScope AI reduces this exploration effort by providing a centralized repository understanding workflow.

```text
GitHub Repository
       ↓
Repository Analysis
       ↓
Architecture Overview
       ↓
Dependency Graph
       ↓
File Explorer
       ↓
AI File Explanation
```

---

## ✨ Features

### 🔍 Repository Analysis

Analyze a public GitHub repository and generate:

- Project overview
- Technology stack
- Architecture observations
- Important files
- Code quality observations
- Potential issues
- Improvement suggestions

The repository analysis uses evidence extracted from repository files and configuration.

---

### 🏗️ Architecture Overview

CodeScope AI identifies common project structures such as:

- Pages
- Components
- Hooks
- Context/state
- Routers
- Services
- APIs
- Utilities
- Authentication modules
- Configuration files

---

### 🔗 Dependency Graph

CodeScope AI analyzes local JavaScript and TypeScript imports and visualizes file relationships using React Flow.

Supported source files include:

```text
.js
.jsx
.ts
.tsx
```

The dependency graph provides:

- File nodes
- Dependency edges
- Import relationships
- Interactive navigation
- Graph controls
- Repository dependency statistics

---

### 📁 File Explorer

Browse analyzed repository files directly inside CodeScope AI.

Users can:

- Browse files by folder
- Select individual files
- View source code
- Inspect repository structure
- Switch between files quickly

---

### 🤖 AI File Explanation

Select any analyzed file and ask CodeScope AI to explain it.

The explanation includes:

- Purpose
- Summary
- Key points
- Imports
- Exports
- Dependencies

Example:

```text
Select File
    ↓
Explain File
    ↓
AI File Explanation
```

---

## 🧠 AI Architecture

CodeScope AI separates deterministic repository analysis from AI interpretation.

```text
GitHub Repository
        │
        ▼
     GitHub API
        │
        ▼
Repository File Filtering
        │
        ├───────────────┐
        ▼               ▼
Deterministic       Dependency
Analysis             Analysis
        │               │
        └───────┬───────┘
                ▼
          CodeScope AI
                │
                ▼
        AI Interpretation
                │
                ▼
          File Explanation
```

The deterministic analysis remains the primary source of repository evidence.

---

## 🛠️ Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Flow (`@xyflow/react`)
- Lucide React

### Backend

- Python
- FastAPI
- Uvicorn
- Requests
- python-dotenv

### AI

- Ollama
- Qwen2.5-Coder for local development
- Ollama Cloud
- gpt-oss:120b for production

### External Services

- GitHub API
- Vercel
- Render
- Ollama Cloud

---

## 📂 Project Structure

```text
CodeScope-AI/
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── dependency_graph_service.py
│   │   │   ├── evidence_service.py
│   │   │   ├── file_filter_service.py
│   │   │   ├── github_service.py
│   │   │   └── repository_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   └── components/
│   │       ├── architecture/
│   │       ├── dependency/
│   │       ├── explorer/
│   │       └── home/
│   │
│   └── package.json
│
└── README.md
```

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/DECODEXJAYANT/CodeScope-AI.git
cd CodeScope-AI
```

---

### 2. Backend Setup

```powershell
cd backend

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create:

```text
backend/.env
```

using:

```text
backend/.env.example
```

Then start the backend:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

---

### 3. Frontend Setup

Open a second terminal:

```powershell
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 🔐 Environment Variables

Create:

```text
backend/.env
```

Example:

```env
GITHUB_TOKEN=

AI_PROVIDER=ollama-local

OLLAMA_LOCAL_URL=http://localhost:11434/api/generate
OLLAMA_LOCAL_MODEL=qwen2.5-coder:1.5b

OLLAMA_CLOUD_URL=https://ollama.com/api/generate
OLLAMA_CLOUD_MODEL=gpt-oss:120b
OLLAMA_API_KEY=
```

Never commit real secrets.

Use:

```text
backend/.env.example
```

as the configuration template.

---

## 🌐 Production Deployment

### Frontend

Deployed using:

```text
Vercel
```

### Backend

Deployed using:

```text
Render
```

### AI

Production AI inference uses:

```text
Ollama Cloud
```

Production architecture:

```text
                Vercel
                  │
                  ▼
          React / TypeScript
                  │
                  ▼
              Render
                  │
          ┌───────┴────────┐
          │                │
          ▼                ▼
      GitHub API      Ollama Cloud
                          │
                          ▼
                     gpt-oss:120b
```

---

## 🔌 API Endpoints

### Health

```http
GET /api/health
```

### Repository Analysis

```http
POST /api/analyze
```

### File

```http
GET /api/file
```

### Repository Files

```http
GET /api/files
```

### Repository Content

```http
GET /api/repository
```

### AI Analysis

```http
GET /api/ai-analyze
```

### Dependency Graph

```http
GET /api/dependency-graph
```

### Explain File

```http
GET /api/explain-file
```

---

## 🧪 Tested Repositories

CodeScope AI has been tested against repositories of different sizes and structures, including:

- React applications
- JavaScript repositories
- TypeScript repositories
- Large repositories and monorepos

Example:

```text
Microsoft Fluent UI
```

with more than 20,000 repository files successfully processed through the analysis pipeline.

---

## ⚠️ Current Limitations

The current MVP intentionally focuses on fast repository understanding.

Current limitations include:

- Repository-level analysis uses a selected subset of files.
- Dependency graph extraction currently focuses on JavaScript/TypeScript local imports.
- Architecture detection is heuristic and evidence-based.
- AI file explanations depend on the configured Ollama provider.
- Very large repositories may require more advanced file-selection strategies.

---

## 🔮 Future Improvements

- Better large-repository sampling
- Python dependency analysis
- Multi-language dependency graphs
- Repository-wide AI chat
- Code search
- Call-graph analysis
- Security analysis
- Test analysis
- Pull request analysis
- Commit history analysis
- Code impact analysis

---

## 📊 Project Status

**Status: Actively Developed**

Current working features:

- GitHub repository analysis
- Technology detection
- Architecture overview
- Dependency graph
- File explorer
- Source-code viewer
- AI file explanation
- Local Ollama inference
- Ollama Cloud inference
- Production deployment

---

## 👨‍💻 Author

**Jayant Kumar**

M.Tech Computer Science & Engineering