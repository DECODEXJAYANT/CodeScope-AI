function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Code<span className="text-blue-500">Scope</span>
            <span className="text-slate-400"> AI</span>
          </h1>
        </div>

        {/* Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
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
            Docs
          </a>

          <a href="#" className="text-slate-400 transition hover:text-white">
            About
          </a>
        </nav>

        {/* CTA */}
        <a
  href="#analyze"
  className="rounded-xl bg-blue-600 px-5 py-2 font-semibold text-white transition hover:bg-blue-500"
>
  Analyze Repository →
</a>
      </div>
    </header>
  );
}

export default Navbar;
