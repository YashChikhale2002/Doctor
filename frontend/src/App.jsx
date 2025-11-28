import { useEffect, useState } from "react";

export default function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/health")
      .then((res) => res.json())
      .then((data) => setApiStatus(data))
      .catch((err) => setApiStatus({ error: String(err) }))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">
          Healthcare Platform
        </h1>
        <span className="text-xs text-slate-400">
          React + Tailwind 4 + Flask + PostgreSQL
        </span>
      </header>

      <main className="p-6 space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs font-medium text-slate-400">API Status</p>
            <p className="mt-2 text-lg font-semibold">
              {loading
                ? "Checking..."
                : apiStatus?.status === "healthy" || apiStatus?.status === "ok"
                ? "Connected"
                : "Error"}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              /api/health from Flask backend
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs font-medium text-slate-400">Facilities</p>
            <p className="mt-2 text-lg font-semibold">Coming soon</p>
            <p className="mt-1 text-xs text-slate-400">
              Multi-tenant hospitals, clinics, labs, etc.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs font-medium text-slate-400">
              Commission Engine
            </p>
            <p className="mt-2 text-lg font-semibold">Design Ready</p>
            <p className="mt-1 text-xs text-slate-400">
              Online + cash settlements with RLS.
            </p>
          </div>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold tracking-tight">
              Raw /api/health response
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
              Debug
            </span>
          </div>
          <pre className="text-xs whitespace-pre-wrap break-all bg-slate-950/70 rounded-lg p-3 border border-slate-800 overflow-x-auto">
            {loading
              ? "Loading..."
              : JSON.stringify(apiStatus, null, 2) || "No data"}
          </pre>
        </section>
      </main>
    </div>
  );
}
