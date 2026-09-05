import HealthStatus from "./HealthStatus";

/**
 * Phase 0 placeholder shell. The real navigation (Overview, Live Protection,
 * Incidents, Attack Lab, Dataset Explorer, Models, Languages, Evaluations,
 * Settings — Design.md section 8) is built in Phase 12.
 */
export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <h1 className="text-2xl font-semibold text-slate-100">VaaniRakshak</h1>
      <p className="mt-1 text-slate-400">Phase 0 — project foundation</p>
      <div className="mt-6 max-w-sm">
        <HealthStatus />
      </div>
    </div>
  );
}
