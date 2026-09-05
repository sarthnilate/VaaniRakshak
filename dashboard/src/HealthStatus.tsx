import { useEffect, useState } from "react";

type ReadyBody = {
  status: "ok" | "degraded";
  dependencies: { redis: string; database: string };
};

/**
 * Phase 0 placeholder: proves the dashboard shell can reach the gateway's
 * health endpoint. The real Live Security Command Center (Phase 12) reads
 * risk_update events over WebSocket instead of polling REST.
 */
export default function HealthStatus() {
  const [state, setState] = useState<"loading" | "ok" | "unreachable">("loading");
  const [detail, setDetail] = useState<ReadyBody | null>(null);

  useEffect(() => {
    const base = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
    fetch(`${base}/v1/health/ready`)
      .then((r) => r.json())
      .then((body: ReadyBody) => {
        setDetail(body);
        setState("ok");
      })
      .catch(() => setState("unreachable"));
  }, []);

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900 p-4 text-slate-100">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
        Gateway status
      </h2>
      {state === "loading" && <p className="mt-2">Checking backend...</p>}
      {state === "unreachable" && (
        <p className="mt-2 text-critical">Backend unreachable — is docker compose up?</p>
      )}
      {state === "ok" && detail && (
        <ul className="mt-2 space-y-1 text-sm">
          <li>Overall: {detail.status}</li>
          <li>Redis: {detail.dependencies.redis}</li>
          <li>Database: {detail.dependencies.database}</li>
        </ul>
      )}
    </div>
  );
}
