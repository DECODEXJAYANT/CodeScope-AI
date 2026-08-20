import { useState, type ReactNode } from "react";

import {
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  FileCode2,
  Layers3,
  Code2,
  FolderSearch,
} from "lucide-react";

import {
  analyzeRepository,
  getDependencyGraph,
} from "../../api/client";

import DependencyGraph from "../dependency/DependencyGraph";
import ArchitectureOverview from "../architecture/ArchitectureOverview";
import FileExplorer from "../explorer/FileExplorer";


// ============================================================
// TYPES
// ============================================================

type Technology = {
  technology: string;
  evidence: string;
};

type ImportantFile = {
  file: string;
  role: string;
  evidence?: string;
};

type Analysis = {
  project_overview?: string;
  technology_stack?: Technology[];
  architecture?: string[];
  important_files?: ImportantFile[];
  code_quality?: string[];
  potential_issues?: string[];
  improvement_suggestions?: string[];
};

type DependencyNode = {
  id: string;
  type: string;
  label: string;
  category?: string;
  path?: string;
};

type DependencyEdge = {
  source: string;
  target: string;
  import?: string;
};

type DependencyGraphData = {
  status: string;
  repository_url: string;
  total_files: number;
  analyzed_files: number;
  nodes: DependencyNode[];
  edges: DependencyEdge[];
};


// ============================================================
// HERO COMPONENT
// ============================================================

function Hero() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [message, setMessage] = useState("");

  const [analysis, setAnalysis] =
    useState<Analysis | null>(null);

  const [loading, setLoading] = useState(false);

  const [dependencyGraph, setDependencyGraph] =
    useState<DependencyGraphData | null>(null);

  const [graphLoading, setGraphLoading] =
    useState(false);


  // ==========================================================
  // ANALYZE REPOSITORY
  // ==========================================================

  const handleAnalyze = async () => {
    const cleanUrl = repositoryUrl.trim();

    // --------------------------------------------------------
    // Validate empty URL
    // --------------------------------------------------------

    if (!cleanUrl) {
      setMessage(
        "Please enter a GitHub repository URL."
      );

      return;
    }

    // --------------------------------------------------------
    // Validate GitHub URL
    // --------------------------------------------------------

    if (!cleanUrl.includes("github.com")) {
      setMessage(
        "Please enter a valid GitHub repository URL."
      );

      return;
    }

    // --------------------------------------------------------
    // Start loading
    // --------------------------------------------------------

    setLoading(true);
    setGraphLoading(true);

    setMessage("");
    setAnalysis(null);
    setDependencyGraph(null);

    try {
      // ======================================================
      // STEP 1: AI ANALYSIS
      // ======================================================

      const analysisResponse =
        await analyzeRepository(cleanUrl);

      setAnalysis(
        analysisResponse.analysis
      );


      // ======================================================
      // STEP 2: DEPENDENCY GRAPH
      // ======================================================

      const graphData =
        await getDependencyGraph(cleanUrl);

      setDependencyGraph(graphData);


      // ======================================================
      // SUCCESS MESSAGE
      // ======================================================

      setMessage(
        "Repository analysis completed successfully."
      );

    } catch (error) {
      console.error(error);

      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to analyze the repository."
      );

    } finally {
      setLoading(false);
      setGraphLoading(false);
    }
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <section className="relative overflow-hidden">

      {/* ======================================================
          BACKGROUND GLOW
          ====================================================== */}

      <div className="pointer-events-none absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 rounded-full bg-blue-600/10 blur-3xl" />


      <div className="relative mx-auto flex max-w-6xl flex-col items-center px-6 py-24 text-center">


        {/* ====================================================
            BADGE
            ==================================================== */}

        <p className="mb-6 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-400">
          AI-Powered Code Understanding
        </p>


        {/* ====================================================
            HEADING
            ==================================================== */}

        <h1 className="text-5xl font-extrabold leading-tight text-white md:text-7xl">
          Understand Any

          <span className="block text-blue-500">
            Codebase in Minutes
          </span>
        </h1>


        {/* ====================================================
            DESCRIPTION
            ==================================================== */}

        <p className="mt-8 max-w-3xl text-lg leading-8 text-slate-400">
          Explore unfamiliar repositories with AI-powered
          architecture visualization, dependency analysis,
          and intelligent code explanations—all in one place.
        </p>


        {/* ====================================================
            REPOSITORY ANALYZER
            ==================================================== */}

        <div className="mt-14 flex w-full max-w-4xl flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900/80 p-4 shadow-2xl md:flex-row">

          <input
            type="url"
            value={repositoryUrl}
            onChange={(event) =>
              setRepositoryUrl(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !loading
              ) {
                handleAnalyze();
              }
            }}
            placeholder="Paste a public GitHub repository URL..."
            disabled={loading}
            className="flex-1 rounded-xl bg-slate-950 px-5 py-4 text-white outline-none placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50 disabled:opacity-60"
          />


          <button
            type="button"
            onClick={handleAnalyze}
            disabled={loading}
            className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-7 py-4 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? "Analyzing..."
              : "Analyze Repository"}

            {!loading && (
              <ArrowRight size={18} />
            )}
          </button>

        </div>


        {/* ====================================================
            LOADING
            ==================================================== */}

        {loading && (
          <div className="mt-8 flex items-center gap-3 text-sm text-slate-400">

            <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-blue-500" />

            <span>
              CodeScope AI is analyzing the repository...
            </span>

          </div>
        )}


        {/* ====================================================
            STATUS MESSAGE
            ==================================================== */}

        {!loading && message && (
          <p className="mt-4 text-sm text-blue-400">
            {message}
          </p>
        )}


        {/* ====================================================
            AI ANALYSIS
            ==================================================== */}

        {analysis && (
          <div className="mt-12 w-full max-w-5xl text-left">

            {/* ------------------------------------------------
                ANALYSIS HEADER
                ------------------------------------------------ */}

            <div className="mb-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div className="flex items-center gap-3">

                  <div className="rounded-xl bg-blue-500/10 p-3">

                    <FolderSearch
                      size={24}
                      className="text-blue-400"
                    />

                  </div>


                  <div>

                    <h2 className="text-2xl font-bold text-white">
                      AI Repository Analysis
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      Generated by CodeScope AI
                    </p>

                  </div>

                </div>


                <span className="flex w-fit items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-3 py-1 text-xs font-medium text-green-400">

                  <CheckCircle2 size={14} />

                  Analysis Complete

                </span>

              </div>


              <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/50 px-4 py-3">

                <p className="truncate text-sm text-slate-400">
                  {repositoryUrl}
                </p>

              </div>

            </div>


            {/* ------------------------------------------------
                PROJECT OVERVIEW
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<Layers3 size={20} />}
              title="Project Overview"
            >

              <p className="text-sm leading-7 text-slate-300">
                {analysis.project_overview ||
                  "Not enough information"}
              </p>

            </AnalysisCard>


            {/* ------------------------------------------------
                TECHNOLOGY STACK
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<Code2 size={20} />}
              title="Technology Stack"
            >

              {analysis.technology_stack &&
              analysis.technology_stack.length > 0 ? (

                <div className="grid gap-4 md:grid-cols-2">

                  {analysis.technology_stack.map(
                    (item, index) => (

                      <div
                        key={`${item.technology}-${index}`}
                        className="rounded-xl border border-slate-800 bg-slate-950/60 p-4"
                      >

                        <h4 className="font-semibold text-white">
                          {item.technology}
                        </h4>

                        <p className="mt-2 text-sm leading-6 text-slate-400">
                          {item.evidence}
                        </p>

                      </div>

                    )
                  )}

                </div>

              ) : (

                <p className="text-sm text-slate-500">
                  Not enough information
                </p>

              )}

            </AnalysisCard>


            {/* ------------------------------------------------
                ARCHITECTURE FROM AI ANALYSIS
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<Layers3 size={20} />}
              title="Architecture"
            >

              <BulletList
                items={analysis.architecture}
              />

            </AnalysisCard>


            {/* ------------------------------------------------
                IMPORTANT FILES
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<FileCode2 size={20} />}
              title="Important Files"
            >

              {analysis.important_files &&
              analysis.important_files.length > 0 ? (

                <div className="space-y-3">

                  {analysis.important_files.map(
                    (item, index) => (

                      <div
                        key={`${item.file}-${index}`}
                        className="rounded-xl border border-slate-800 bg-slate-950/60 p-4"
                      >

                        <code className="break-all text-sm font-medium text-blue-400">
                          {item.file}
                        </code>


                        <p className="mt-2 text-sm leading-6 text-slate-400">
                          {item.role}
                        </p>


                        {item.evidence && (
                          <p className="mt-2 text-xs leading-5 text-slate-500">
                            {item.evidence}
                          </p>
                        )}

                      </div>

                    )
                  )}

                </div>

              ) : (

                <p className="text-sm text-slate-500">
                  Not enough information
                </p>

              )}

            </AnalysisCard>


            {/* ------------------------------------------------
                CODE QUALITY
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<CheckCircle2 size={20} />}
              title="Code Quality"
            >

              <BulletList
                items={analysis.code_quality}
              />

            </AnalysisCard>


            {/* ------------------------------------------------
                POTENTIAL ISSUES
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<AlertTriangle size={20} />}
              title="Potential Issues"
              iconClassName="text-yellow-400"
            >

              <BulletList
                items={analysis.potential_issues}
              />

            </AnalysisCard>


            {/* ------------------------------------------------
                IMPROVEMENT SUGGESTIONS
                ------------------------------------------------ */}

            <AnalysisCard
              icon={<Lightbulb size={20} />}
              title="Improvement Suggestions"
              iconClassName="text-blue-400"
            >

              <BulletList
                items={
                  analysis.improvement_suggestions
                }
              />

            </AnalysisCard>

          </div>
        )}


        {/* ====================================================
            DEPENDENCY GRAPH LOADING
            ==================================================== */}

        {graphLoading && (
          <div className="mt-10 w-full max-w-6xl text-left">

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8">

              <div className="flex items-center gap-3">

                <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-600 border-t-blue-500" />


                <div>

                  <h2 className="text-xl font-bold text-white">
                    Generating Dependency Graph
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Mapping relationships between repository files...
                  </p>

                </div>

              </div>

            </div>

          </div>
        )}


        {/* ====================================================
            VISUALIZATION RESULTS
            ==================================================== */}

        {dependencyGraph && (
          <div className="mt-12 w-full max-w-6xl text-left">

            {/* ==================================================
                ARCHITECTURE OVERVIEW
                ================================================== */}

            <div className="mb-12">

              <div className="mb-6">

                <div className="flex items-center gap-3">

                  <div className="rounded-xl bg-blue-500/10 p-3">

                    <Layers3
                      size={22}
                      className="text-blue-400"
                    />

                  </div>


                  <div>

                    <h2 className="text-2xl font-bold text-white">
                      Architecture Overview
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      High-level view of how the repository is structured.
                    </p>

                  </div>

                </div>

              </div>


              <ArchitectureOverview
                nodes={dependencyGraph.nodes}
                edges={dependencyGraph.edges}
              />

            </div>


            {/* ==================================================
                REPOSITORY DEPENDENCY GRAPH
                ================================================== */}

            <div className="mb-12">

              {/* GRAPH HEADER */}

              <div className="mb-6">

                <div className="flex items-center gap-3">

                  <div className="rounded-xl bg-blue-500/10 p-3">

                    <FolderSearch
                      size={22}
                      className="text-blue-400"
                    />

                  </div>


                  <div>

                    <h2 className="text-2xl font-bold text-white">
                      Repository Dependency Graph
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      Visual representation of file dependencies.
                    </p>

                  </div>

                </div>

              </div>


              {/* GRAPH STATISTICS */}

              <div className="mb-6 grid gap-4 sm:grid-cols-3">

                <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">

                  <p className="text-sm text-slate-400">
                    Repository Files
                  </p>

                  <p className="mt-1 text-2xl font-bold text-white">
                    {dependencyGraph.total_files}
                  </p>

                </div>


                <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">

                  <p className="text-sm text-slate-400">
                    Analyzed Files
                  </p>

                  <p className="mt-1 text-2xl font-bold text-white">
                    {dependencyGraph.analyzed_files}
                  </p>

                </div>


                <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">

                  <p className="text-sm text-slate-400">
                    Dependencies
                  </p>

                  <p className="mt-1 text-2xl font-bold text-white">
                    {dependencyGraph.edges?.length ?? 0}
                  </p>

                </div>

              </div>


              {/* GRAPH */}

              <DependencyGraph
                nodes={dependencyGraph.nodes ?? []}
                edges={dependencyGraph.edges ?? []}
              />

            </div>


            {/* ==================================================
                REPOSITORY FILE EXPLORER
                ================================================== */}

            <div className="mt-12">

              <FileExplorer
                repositoryUrl={repositoryUrl}
                files={dependencyGraph.nodes.map(
                  (node) => ({
                    path:
                      node.path ||
                      node.id,
                  })
                )}
              />

            </div>

          </div>
        )}

      </div>
    </section>
  );
}


// ============================================================
// ANALYSIS CARD
// ============================================================

function AnalysisCard({
  title,
  icon,
  children,
  iconClassName = "text-blue-400",
}: {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  iconClassName?: string;
}) {
  return (
    <div className="mb-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">

      <div className="mb-5 flex items-center gap-3 border-b border-slate-800 pb-4">

        <div
          className={`rounded-lg bg-slate-950 p-2 ${iconClassName}`}
        >
          {icon}
        </div>


        <h3 className="text-lg font-semibold text-white">
          {title}
        </h3>

      </div>


      {children}

    </div>
  );
}


// ============================================================
// BULLET LIST
// ============================================================

function BulletList({
  items,
}: {
  items?: string[];
}) {
  if (!items || items.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Not enough information
      </p>
    );
  }


  return (
    <div className="space-y-3">

      {items.map((item, index) => (

        <div
          key={`${item}-${index}`}
          className="flex gap-3 rounded-xl border border-slate-800 bg-slate-950/50 p-4"
        >

          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />


          <p className="text-sm leading-7 text-slate-300">
            {item}
          </p>

        </div>

      ))}

    </div>
  );
}


export default Hero;