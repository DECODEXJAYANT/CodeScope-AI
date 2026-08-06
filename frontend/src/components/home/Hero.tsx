function Hero() {
  return (
    <section className="mx-auto flex max-w-5xl flex-col items-center px-6 py-24 text-center">
      <p className="mb-4 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1 text-sm text-blue-400">
        AI-Powered Code Intelligence
      </p>

      <h1 className="text-5xl font-extrabold leading-tight text-white md:text-7xl">
        Understand Any
        <span className="block text-blue-500">
          Codebase in Minutes
        </span>
      </h1>

      <p className="mt-8 max-w-2xl text-lg text-slate-400">
        Analyze GitHub repositories using AI. Explore architecture,
        dependencies, code metrics, and intelligent explanations—all in one
        place.
      </p>
    </section>
  );
}

export default Hero;