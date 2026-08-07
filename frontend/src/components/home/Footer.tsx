function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="mx-auto max-w-7xl px-6 py-16">

        <div className="grid gap-12 md:grid-cols-3">

          {/* Brand */}
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-white">
              Code<span className="text-blue-500">Scope</span>
              <span className="text-slate-400"> AI</span>
            </h2>

            <p className="mt-4 max-w-sm leading-7 text-slate-400">
              Understand unfamiliar codebases faster with AI-powered
              architecture analysis, dependency insights, and code
              explanations.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-white">
              Product
            </h3>

            <div className="mt-5 flex flex-col gap-3">
              <a
                href="#features"
                className="text-slate-400 transition hover:text-white"
              >
                Features
              </a>

              <a
                href="#how-it-works"
                className="text-slate-400 transition hover:text-white"
              >
                How It Works
              </a>

              <a
                href="#analyze"
                className="text-slate-400 transition hover:text-white"
              >
                Analyze Repository
              </a>
            </div>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-white">
              Resources
            </h3>

            <div className="mt-5 flex flex-col gap-3">
              <a
                href="#"
                className="text-slate-400 transition hover:text-white"
              >
                Documentation
              </a>

              <a
                href="#"
                className="text-slate-400 transition hover:text-white"
              >
                GitHub
              </a>

              <a
                href="#"
                className="text-slate-400 transition hover:text-white"
              >
                API
              </a>
            </div>
          </div>

        </div>

        {/* Bottom */}
        <div className="mt-16 flex flex-col gap-4 border-t border-slate-800 pt-8 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
          <p>
            © 2026 CodeScope AI. Built for developers.
          </p>

          <p>
            AI-powered code understanding.
          </p>
        </div>

      </div>
    </footer>
  );
}

export default Footer;