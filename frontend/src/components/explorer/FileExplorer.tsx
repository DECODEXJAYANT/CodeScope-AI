import { useEffect, useState } from "react";

import {
  FileCode2,
  Folder,
  Loader2,
  Sparkles,
} from "lucide-react";

import {
  getRepositoryFile,
  explainRepositoryFile,
} from "../../api/client";


// ============================================================
// TYPES
// ============================================================

type RepositoryFile = {
  path: string;
  size?: number;
};

type FileExplorerProps = {
  repositoryUrl: string;
  files: RepositoryFile[];
};

type FileExplanation = {
  purpose?: string;
  summary?: string;
  imports?: string[];
  exports?: string[];
  key_points?: string[];
  dependencies?: string[];
};


// ============================================================
// HELPERS
// ============================================================

function getFileName(path: string): string {
  return path.split("/").pop() || path;
}


function getParentFolder(path: string): string {
  const parts = path.split("/");

  if (parts.length <= 1) {
    return "root";
  }

  return parts.slice(0, -1).join("/");
}


// ============================================================
// COMPONENT
// ============================================================

function FileExplorer({
  repositoryUrl,
  files,
}: FileExplorerProps) {
  // ----------------------------------------------------------
  // Selected file
  // ----------------------------------------------------------

  const [selectedFile, setSelectedFile] =
    useState<string | null>(null);

  // ----------------------------------------------------------
  // File content
  // ----------------------------------------------------------

  const [fileContent, setFileContent] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  // ----------------------------------------------------------
  // AI explanation
  // ----------------------------------------------------------

  const [explanation, setExplanation] =
    useState<FileExplanation | null>(null);

  const [explainLoading, setExplainLoading] =
    useState(false);

  const [explainError, setExplainError] =
    useState("");


  // ==========================================================
  // GROUP FILES BY FOLDER
  // ==========================================================

  const groupedFiles = files.reduce<
    Record<string, RepositoryFile[]>
  >((groups, file) => {
    const folder = getParentFolder(
      file.path
    );

    if (!groups[folder]) {
      groups[folder] = [];
    }

    groups[folder].push(file);

    return groups;
  }, {});


  // ==========================================================
  // LOAD SELECTED FILE
  // ==========================================================

  useEffect(() => {
    if (!selectedFile) {
      setFileContent("");
      setError("");
      setExplanation(null);
      setExplainError("");

      return;
    }

    // Capture the narrowed value so TypeScript knows
    // this is definitely a string inside the async function.
    const filePath = selectedFile;

    let cancelled = false;

    async function loadFile() {
      setLoading(true);
      setError("");
      setFileContent("");

      // Clear previous AI explanation when switching files.
      setExplanation(null);
      setExplainError("");

      try {
        const data = await getRepositoryFile(
          repositoryUrl,
          filePath
        );

        if (cancelled) {
          return;
        }

        setFileContent(
          data.file?.content || ""
        );
      } catch (error) {
        if (cancelled) {
          return;
        }

        setError(
          error instanceof Error
            ? error.message
            : "Failed to load file."
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadFile();

    return () => {
      cancelled = true;
    };
  }, [repositoryUrl, selectedFile]);


  // ==========================================================
  // EXPLAIN SELECTED FILE
  // ==========================================================

  const handleExplainFile = async () => {
    if (!selectedFile) {
      return;
    }

    setExplainLoading(true);
    setExplainError("");
    setExplanation(null);

    try {
      const data =
        await explainRepositoryFile(
          repositoryUrl,
          selectedFile
        );

      setExplanation(
        data.explanation || null
      );
    } catch (error) {
      setExplainError(
        error instanceof Error
          ? error.message
          : "Failed to explain file."
      );
    } finally {
      setExplainLoading(false);
    }
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 shadow-xl">

      {/* ====================================================
          HEADER
          ==================================================== */}

      <div className="border-b border-slate-800 px-6 py-5">

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-blue-500/10 p-3">

            <FileCode2
              size={22}
              className="text-blue-400"
            />

          </div>

          <div>

            <h2 className="text-2xl font-bold text-white">
              Repository File Explorer
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Browse analyzed repository files, inspect
              source code, and get AI explanations.
            </p>

          </div>

        </div>

      </div>


      {/* ====================================================
          CONTENT
          ==================================================== */}

      <div className="grid min-h-150 grid-cols-1 lg:grid-cols-[320px_1fr]">

        {/* ==================================================
            FILE LIST
            ================================================== */}

        <div className="border-b border-slate-800 bg-slate-950/60 lg:border-b-0 lg:border-r">

          <div className="border-b border-slate-800 px-4 py-3">

            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Analyzed Files
            </p>

            <p className="mt-1 text-sm text-slate-300">
              {files.length} files
            </p>

          </div>


          <div className="max-h-140 overflow-y-auto p-3">

            {files.length === 0 ? (

              <p className="px-3 py-5 text-sm text-slate-500">
                No files available.
              </p>

            ) : (

              Object.entries(groupedFiles)
                .sort(([a], [b]) =>
                  a.localeCompare(b)
                )
                .map(
                  ([folder, folderFiles]) => (

                    <div
                      key={folder}
                      className="mb-4"
                    >

                      {/* Folder */}

                      <div className="mb-2 flex items-center gap-2 px-2">

                        <Folder
                          size={14}
                          className="text-slate-500"
                        />

                        <span className="truncate text-xs font-medium text-slate-500">
                          {folder}
                        </span>

                      </div>


                      {/* Files */}

                      <div className="space-y-1">

                        {folderFiles
                          .sort((a, b) =>
                            a.path.localeCompare(
                              b.path
                            )
                          )
                          .map((file) => {

                            const isSelected =
                              selectedFile ===
                              file.path;

                            return (
                              <button
                                type="button"
                                key={file.path}
                                onClick={() =>
                                  setSelectedFile(
                                    file.path
                                  )
                                }
                                className={`w-full rounded-lg px-3 py-2 text-left transition ${
                                  isSelected
                                    ? "bg-blue-500/10 text-blue-400"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                                }`}
                              >

                                <div className="flex items-start gap-2">

                                  <FileCode2
                                    size={14}
                                    className="mt-0.5 shrink-0"
                                  />

                                  <div className="min-w-0">

                                    <p className="truncate text-sm">
                                      {getFileName(
                                        file.path
                                      )}
                                    </p>

                                    <p className="truncate text-[11px] text-slate-600">
                                      {file.path}
                                    </p>

                                  </div>

                                </div>

                              </button>
                            );
                          })}

                      </div>

                    </div>
                  )
                )
            )}

          </div>

        </div>


        {/* ==================================================
            FILE VIEWER
            ================================================== */}

        <div className="min-w-0">

          {/* ==================================================
              NO FILE SELECTED
              ================================================== */}

          {!selectedFile && (

            <div className="flex min-h-140 items-center justify-center px-6">

              <div className="max-w-md text-center">

                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-800 bg-slate-950">

                  <FileCode2
                    size={24}
                    className="text-slate-600"
                  />

                </div>

                <h3 className="text-lg font-semibold text-white">
                  Select a file
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Choose a repository file from the
                  left panel to inspect its source code
                  and generate an AI explanation.
                </p>

              </div>

            </div>
          )}


          {/* ==================================================
              SELECTED FILE
              ================================================== */}

          {selectedFile && (

            <div className="flex min-h-140 flex-col">

              {/* =================================================
                  FILE HEADER
                  ================================================= */}

              <div className="flex items-center justify-between gap-4 border-b border-slate-800 px-6 py-4">

                <p className="truncate font-mono text-sm text-blue-400">
                  {selectedFile}
                </p>


                <button
                  type="button"
                  onClick={handleExplainFile}
                  disabled={
                    explainLoading ||
                    loading
                  }
                  className="flex shrink-0 items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                >

                  {explainLoading ? (
                    <>
                      <Loader2
                        size={15}
                        className="animate-spin"
                      />

                      Explaining...
                    </>
                  ) : (
                    <>
                      <Sparkles size={15} />

                      Explain File
                    </>
                  )}

                </button>

              </div>


              {/* =================================================
                  EXPLANATION ERROR
                  ================================================= */}

              {explainError && (

                <div className="border-b border-red-900/40 bg-red-950/20 px-6 py-4">

                  <p className="text-sm text-red-400">
                    {explainError}
                  </p>

                </div>
              )}


              {/* =================================================
                  AI EXPLANATION
                  ================================================= */}

              {explanation && (

                <div className="border-b border-slate-800 bg-slate-900/60 p-6">

                  <div className="mb-5 flex items-center gap-2">

                    <Sparkles
                      size={18}
                      className="text-blue-400"
                    />

                    <h3 className="text-lg font-semibold text-white">
                      AI File Explanation
                    </h3>

                  </div>


                  <div className="space-y-5">

                    {/* Purpose */}

                    <div>

                      <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Purpose
                      </p>

                      <p className="text-sm leading-6 text-slate-300">
                        {explanation.purpose ||
                          "Not enough information"}
                      </p>

                    </div>


                    {/* Summary */}

                    <div>

                      <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Summary
                      </p>

                      <p className="text-sm leading-6 text-slate-300">
                        {explanation.summary ||
                          "Not enough information"}
                      </p>

                    </div>


                    {/* Key Points */}

                    <div>

                      <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Key Points
                      </p>

                      {explanation.key_points &&
                      explanation.key_points.length > 0 ? (

                        <div className="space-y-2">

                          {explanation.key_points.map(
                            (
                              item,
                              index
                            ) => (

                              <div
                                key={`${item}-${index}`}
                                className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-300"
                              >
                                {item}
                              </div>

                            )
                          )}

                        </div>

                      ) : (

                        <p className="text-sm text-slate-500">
                          Not enough information
                        </p>

                      )}

                    </div>


                    {/* Imports / Exports */}

                    <div className="grid gap-5 md:grid-cols-2">

                      {/* Imports */}

                      <div>

                        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                          Imports
                        </p>

                        {explanation.imports &&
                        explanation.imports.length > 0 ? (

                          <div className="space-y-1">

                            {explanation.imports.map(
                              (
                                item,
                                index
                              ) => (

                                <p
                                  key={`${item}-${index}`}
                                  className="break-all font-mono text-xs text-blue-400"
                                >
                                  {item}
                                </p>

                              )
                            )}

                          </div>

                        ) : (

                          <p className="text-sm text-slate-500">
                            None detected
                          </p>

                        )}

                      </div>


                      {/* Exports */}

                      <div>

                        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                          Exports
                        </p>

                        {explanation.exports &&
                        explanation.exports.length > 0 ? (

                          <div className="space-y-1">

                            {explanation.exports.map(
                              (
                                item,
                                index
                              ) => (

                                <p
                                  key={`${item}-${index}`}
                                  className="break-all font-mono text-xs text-green-400"
                                >
                                  {item}
                                </p>

                              )
                            )}

                          </div>

                        ) : (

                          <p className="text-sm text-slate-500">
                            None detected
                          </p>

                        )}

                      </div>

                    </div>


                    {/* Dependencies */}

                    <div>

                      <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Dependencies
                      </p>

                      {explanation.dependencies &&
                      explanation.dependencies.length > 0 ? (

                        <div className="space-y-1">

                          {explanation.dependencies.map(
                            (
                              item,
                              index
                            ) => (

                              <p
                                key={`${item}-${index}`}
                                className="text-sm text-slate-400"
                              >
                                • {item}
                              </p>

                            )
                          )}

                        </div>

                      ) : (

                        <p className="text-sm text-slate-500">
                          None identified
                        </p>

                      )}

                    </div>

                  </div>

                </div>
              )}


              {/* =================================================
                  FILE LOADING
                  ================================================= */}

              {loading && (

                <div className="flex flex-1 items-center justify-center">

                  <div className="flex items-center gap-3 text-sm text-slate-400">

                    <Loader2
                      size={18}
                      className="animate-spin text-blue-400"
                    />

                    Loading file...

                  </div>

                </div>
              )}


              {/* =================================================
                  FILE ERROR
                  ================================================= */}

              {!loading && error && (

                <div className="flex flex-1 items-center justify-center px-6">

                  <div className="max-w-md text-center">

                    <p className="text-sm font-medium text-red-400">
                      {error}
                    </p>

                  </div>

                </div>
              )}


              {/* =================================================
                  SOURCE CODE
                  ================================================= */}

              {!loading &&
                !error &&
                fileContent && (

                  <div className="flex-1 overflow-auto bg-slate-950">

                    <pre className="min-h-full p-6 text-left font-mono text-xs leading-6 text-slate-300">

                      <code>
                        {fileContent}
                      </code>

                    </pre>

                  </div>
                )}


              {/* =================================================
                  EMPTY FILE
                  ================================================= */}

              {!loading &&
                !error &&
                !fileContent && (

                  <div className="flex flex-1 items-center justify-center px-6">

                    <p className="text-sm text-slate-500">
                      This file has no readable content.
                    </p>

                  </div>
                )}

            </div>
          )}

        </div>

      </div>

    </div>
  );
}


export default FileExplorer;