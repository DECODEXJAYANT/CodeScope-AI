function Navbar() {
  return (
    <nav className="w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            Code<span className="text-blue-500">Scope</span> AI
          </h1>
        </div>

        {/* Navigation */}
        <div className="hidden gap-8 text-sm text-slate-300 md:flex">
          <a href="#" className="transition hover:text-white">
            Features
          </a>

          <a href="#" className="transition hover:text-white">
            Docs
          </a>

          <a href="#" className="transition hover:text-white">
            About
          </a>
        </div>

        {/* GitHub Button */}
        <button className="rounded-xl bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700">
          GitHub
        </button>
      </div>
    </nav>
  );
}

export default Navbar;