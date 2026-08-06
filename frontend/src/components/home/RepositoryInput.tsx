function RepositoryInput() {
  return (
    <div className="mt-12 flex w-full max-w-3xl flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl md:flex-row">

      <input
        type="text"
        placeholder="Paste a public GitHub repository URL..."
        className="flex-1 rounded-xl bg-slate-950 px-5 py-4 text-white outline-none placeholder:text-slate-500"
      />

      <button className="rounded-xl bg-blue-600 px-8 py-4 font-semibold text-white transition hover:bg-blue-500">
        Analyze Repository →
      </button>

    </div>
  );
}

export default RepositoryInput;