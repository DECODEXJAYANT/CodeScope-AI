import { useState } from "react";
import { ArrowRight } from "lucide-react";

function Hero() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!repositoryUrl.trim()) {
      setMessage("Please enter a GitHub repository URL.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/analyze?repository_url=" +
          encodeURIComponent(repositoryUrl),
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const data = await response.json();

      setMessage(data.message);
    } catch (error) {
      setMessage("Unable to connect to CodeScope AI backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative overflow-hidden bg-slate-950">
      {/* Background Glow */}
      <div className="absolute left-1/2 top-24 h-80 w-80 -translate-x-1/2 rounded-full bg-blue-600/20 blur-3xl" />

      <div className="relative mx-auto flex max-w-5xl flex-col items-center px-6 py-24 text-center">

        <p className="mb-6 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-400">
          AI-Powered Code Understanding
        </p>

        <h1 className="text-5xl font-extrabold leading-tight text-white md:text-7xl">
          Understand Any
          <span className="block text-blue-500">
            Codebase in Minutes
          </span>
        </h1>

        <p className="mt-8 max-w-3xl text-lg leading-8 text-slate-400">
          Explore unfamiliar repositories with AI-powered architecture
          visualization, dependency analysis, and intelligent code explanations—
          all in one place.
        </p>

        {/* Repository Analyzer */}
        <div className="mt-14 flex w-full max-w-4xl flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900/80 p-4 shadow-2xl md:flex-row">

          <input
            type="url"
            value={repositoryUrl}
            onChange={(event) => setRepositoryUrl(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleAnalyze();
              }
            }}
            placeholder="Paste a public GitHub repository URL..."
            className="flex-1 rounded-xl bg-slate-950 px-5 py-4 text-white outline-none placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500/50"
          />

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-7 py-4 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Analyze Repository"}

            {!loading && <ArrowRight size={18} />}
          </button>
        </div>

        {/* Backend Response */}
        {message && (
          <p className="mt-4 text-sm text-blue-400">
            {message}
          </p>
        )}

      </div>
    </section>
  );
}

export default Hero;