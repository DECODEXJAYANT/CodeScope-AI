import RepositoryInput from "./RepositoryInput";

function Hero() {
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

        <RepositoryInput />
      </div>
    </section>
  );
}

export default Hero;