const features = [
  {
    number: "01",
    title: "Repository Intelligence",
    description:
      "Get an AI-generated overview of an unfamiliar codebase, including its purpose, structure, and major components.",
  },
  {
    number: "02",
    title: "Architecture Explorer",
    description:
      "Understand how folders, modules, services, and major components are organized and connected.",
  },
  {
    number: "03",
    title: "AI Code Assistant",
    description:
      "Ask questions about the repository and get explanations grounded in the actual code.",
  },
  {
    number: "04",
    title: "Dependency & Insights",
    description:
      "Discover dependencies, important files, complexity hotspots, and other useful repository insights.",
  },
];

function Features() {
  return (
    <section
  id="features"
  className="relative scroll-mt-20 bg-slate-950 px-6 py-24"
>
      <div className="mx-auto max-w-7xl">

        {/* Section Header */}
        <div className="mx-auto max-w-3xl text-center">
          <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-blue-500">
            Explore Faster
          </p>

          <h2 className="text-4xl font-bold tracking-tight text-white md:text-5xl">
            Everything you need to
            <span className="text-blue-500"> understand a codebase</span>
          </h2>

          <p className="mt-6 text-lg leading-8 text-slate-400">
            CodeScope AI turns an unfamiliar repository into an understandable
            map of architecture, dependencies, code, and insights.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="mt-16 grid gap-6 md:grid-cols-2">
          {features.map((feature) => (
            <div
              key={feature.number}
              className="group rounded-2xl border border-slate-800 bg-slate-900/60 p-8 transition duration-300 hover:-translate-y-1 hover:border-blue-500/40 hover:bg-slate-900"
            >
              <div className="mb-8 flex items-center justify-between">
                <span className="text-sm font-semibold text-blue-500">
                  {feature.number}
                </span>

                <div className="h-px w-16 bg-slate-800 transition group-hover:bg-blue-500/50" />
              </div>

              <h3 className="text-2xl font-semibold text-white">
                {feature.title}
              </h3>

              <p className="mt-4 leading-7 text-slate-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}

export default Features;