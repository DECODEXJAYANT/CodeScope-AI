const steps = [
  {
    number: "01",
    title: "Paste Repository",
    description:
      "Start by providing a public GitHub repository URL that you want to understand.",
  },
  {
    number: "02",
    title: "Analyze Codebase",
    description:
      "CodeScope AI scans the repository structure, files, dependencies, and relationships.",
  },
  {
    number: "03",
    title: "Build Understanding",
    description:
      "AI transforms the raw codebase into architecture, insights, and intelligent explanations.",
  },
  {
    number: "04",
    title: "Explore & Ask",
    description:
      "Navigate the codebase visually and ask questions about how different parts of the system work.",
  },
];

function HowItWorks() {
  return (
    <section
  id="how-it-works"
  className="relative scroll-mt-20 overflow-hidden bg-slate-950 px-6 py-24"
>
      <div className="mx-auto max-w-7xl">

        {/* Section Header */}
        <div className="mx-auto max-w-3xl text-center">
          <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-blue-500">
            How It Works
          </p>

          <h2 className="text-4xl font-bold tracking-tight text-white md:text-5xl">
            From unfamiliar code to
            <span className="text-blue-500"> understanding</span>
          </h2>

          <p className="mt-6 text-lg leading-8 text-slate-400">
            Go from a GitHub URL to a clear understanding of a codebase in
            just a few steps.
          </p>
        </div>

        {/* Steps */}
        <div className="relative mt-20 grid gap-10 md:grid-cols-4">

          {/* Connecting Line */}
          <div className="absolute left-[12%] right-[12%] top-7 hidden h-px bg-slate-800 md:block" />

          {steps.map((step) => (
            <div
              key={step.number}
              className="relative text-center"
            >
              {/* Number */}
              <div className="relative mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-blue-500/40 bg-slate-950 text-sm font-bold text-blue-500">
                {step.number}
              </div>

              <h3 className="mt-6 text-xl font-semibold text-white">
                {step.title}
              </h3>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                {step.description}
              </p>
            </div>
          ))}

        </div>
      </div>
    </section>
  );
}

export default HowItWorks;