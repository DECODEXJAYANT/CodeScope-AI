import { useEffect, useState } from "react";

import Navbar from "./components/home/Navbar";
import Hero from "./components/home/Hero";
import Features from "./components/home/Features";
import HowItWorks from "./components/home/HowItWorks";
import Footer from "./components/home/Footer";

import { checkBackend } from "./api/client";

function App() {
  const [backendStatus, setBackendStatus] = useState("");

  useEffect(() => {
    checkBackend()
      .then((data) => {
        setBackendStatus(data.message);
      })
      .catch(() => {
        setBackendStatus("Backend connection failed");
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />

      <Hero />

      {/* Temporary backend connection test */}
      <p className="py-4 text-center text-green-400">
        {backendStatus}
      </p>

      <Features />

      <HowItWorks />

      <Footer />
    </div>
  );
}

export default App;