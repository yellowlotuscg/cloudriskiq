"use client";

import { useEffect, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type Health = { status: string; service: string; version: string };

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "4rem 1.5rem" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "0.25rem" }}>CloudRiskIQ</h1>
      <p style={{ opacity: 0.7, marginTop: 0 }}>
        Unified cloud + endpoint + source-control security findings.
      </p>

      <section
        style={{
          marginTop: "2rem",
          padding: "1rem 1.25rem",
          border: "1px solid #243049",
          borderRadius: 12,
          background: "#121933",
        }}
      >
        <h2 style={{ fontSize: "1rem", margin: "0 0 0.5rem" }}>Backend status</h2>
        {health ? (
          <code style={{ color: "#7ee787" }}>
            {health.status} · {health.service} · v{health.version}
          </code>
        ) : error ? (
          <code style={{ color: "#ff7b72" }}>API unreachable: {error}</code>
        ) : (
          <code style={{ opacity: 0.6 }}>checking {API_BASE}/health …</code>
        )}
      </section>
    </main>
  );
}
