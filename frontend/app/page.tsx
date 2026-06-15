"use client";

import { useEffect, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type ControlRef = { framework: string; control_id: string; title: string };
type Finding = {
  id: string;
  source: string;
  title: string;
  severity: string;
  category: string;
  resource: string;
  risk_score: number;
  status: string;
  compliance_scope: string[];
  controls: ControlRef[];
};
type Summary = {
  total: number;
  by_source: Record<string, number>;
  by_severity: { low: number; medium: number; high: number; critical: number };
  by_status: Record<string, number>;
  open_critical_high: number;
  average_risk_score: number;
};
type Coverage = {
  frameworks: string[];
  controls: {
    framework: string;
    control_id: string;
    title: string;
    finding_count: number;
    max_risk_score: number;
  }[];
};

const SEV_COLOR: Record<string, string> = {
  critical: "#ff5c5c",
  high: "#ff9f43",
  medium: "#ffd93d",
  low: "#7ee787",
};

function riskColor(score: number): string {
  if (score >= 90) return "#ff5c5c";
  if (score >= 75) return "#ff9f43";
  if (score >= 50) return "#ffd93d";
  return "#7ee787";
}

const card = {
  border: "1px solid #243049",
  borderRadius: 12,
  background: "#121933",
  padding: "1rem 1.25rem",
} as const;

export default function Home() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [coverage, setCoverage] = useState<Coverage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<string>("");

  useEffect(() => {
    const q = sourceFilter ? `?source=${sourceFilter}` : "";
    Promise.all([
      fetch(`${API_BASE}/summary`).then((r) => r.json()),
      fetch(`${API_BASE}/findings${q}`).then((r) => r.json()),
      fetch(`${API_BASE}/controls`).then((r) => r.json()),
    ])
      .then(([s, f, c]) => {
        setSummary(s);
        setFindings(f.items);
        setCoverage(c);
      })
      .catch((e) => setError(String(e)));
  }, [sourceFilter]);

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: "3rem 1.5rem" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "0.25rem" }}>CloudRiskIQ</h1>
      <p style={{ opacity: 0.7, marginTop: 0 }}>
        Unified cloud + endpoint + source-control findings, risk-scored and mapped
        to NIST CSF / CIS / PCI-DSS / SOX / FISMA controls.
      </p>

      {error && (
        <div style={{ ...card, borderColor: "#ff5c5c", marginTop: "1.5rem" }}>
          <code style={{ color: "#ff7b72" }}>
            API unreachable ({API_BASE}): {error}. Start the backend with{" "}
            <b>uvicorn app.main:app --port 8000</b>.
          </code>
        </div>
      )}

      {summary && (
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
            gap: "1rem",
            marginTop: "1.5rem",
          }}
        >
          <Kpi label="Findings" value={summary.total} />
          <Kpi
            label="Open critical/high"
            value={summary.open_critical_high}
            color="#ff9f43"
          />
          <Kpi label="Avg risk score" value={summary.average_risk_score} />
          <Kpi label="Critical" value={summary.by_severity.critical} color="#ff5c5c" />
          <Kpi label="High" value={summary.by_severity.high} color="#ff9f43" />
        </section>
      )}

      <section style={{ marginTop: "2rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "0.75rem",
          }}
        >
          <h2 style={{ fontSize: "1.1rem", margin: 0 }}>
            Prioritized findings ({findings.length})
          </h2>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            style={{
              background: "#121933",
              color: "#e6e9f2",
              border: "1px solid #243049",
              borderRadius: 8,
              padding: "0.35rem 0.6rem",
            }}
          >
            <option value="">all sources</option>
            <option value="aws">aws</option>
            <option value="azure">azure</option>
            <option value="endpoint">endpoint</option>
            <option value="github">github</option>
          </select>
        </div>

        <div style={{ ...card, padding: 0, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
            <thead>
              <tr style={{ textAlign: "left", background: "#0e1530" }}>
                <Th>Risk</Th>
                <Th>Severity</Th>
                <Th>Source</Th>
                <Th>Finding</Th>
                <Th>Resource</Th>
                <Th>Controls</Th>
              </tr>
            </thead>
            <tbody>
              {findings.map((f) => (
                <tr key={f.id} style={{ borderTop: "1px solid #1c2747" }}>
                  <td style={{ padding: "0.5rem 0.75rem" }}>
                    <span
                      style={{
                        fontWeight: 700,
                        color: riskColor(f.risk_score),
                      }}
                    >
                      {f.risk_score}
                    </span>
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem" }}>
                    <span style={{ color: SEV_COLOR[f.severity] || "#e6e9f2" }}>
                      {f.severity}
                    </span>
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem", opacity: 0.85 }}>{f.source}</td>
                  <td style={{ padding: "0.5rem 0.75rem" }}>{f.title}</td>
                  <td
                    style={{
                      padding: "0.5rem 0.75rem",
                      opacity: 0.7,
                      fontFamily: "ui-monospace, monospace",
                      fontSize: "0.78rem",
                      maxWidth: 240,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                    title={f.resource}
                  >
                    {f.resource}
                  </td>
                  <td style={{ padding: "0.5rem 0.75rem", opacity: 0.85 }}>
                    {f.controls.length}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {coverage && (
        <section style={{ marginTop: "2rem" }}>
          <h2 style={{ fontSize: "1.1rem" }}>
            Control coverage
            <span style={{ opacity: 0.6, fontWeight: 400, fontSize: "0.85rem" }}>
              {"  "}: {coverage.frameworks.join(" · ")}
            </span>
          </h2>
          <div style={{ ...card, padding: 0, overflow: "hidden" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ textAlign: "left", background: "#0e1530" }}>
                  <Th>Framework</Th>
                  <Th>Control</Th>
                  <Th>Title</Th>
                  <Th>Findings</Th>
                  <Th>Max risk</Th>
                </tr>
              </thead>
              <tbody>
                {coverage.controls.map((c, i) => (
                  <tr key={i} style={{ borderTop: "1px solid #1c2747" }}>
                    <td style={{ padding: "0.45rem 0.75rem", opacity: 0.85 }}>{c.framework}</td>
                    <td style={{ padding: "0.45rem 0.75rem", fontWeight: 600 }}>{c.control_id}</td>
                    <td style={{ padding: "0.45rem 0.75rem", opacity: 0.8 }}>{c.title}</td>
                    <td style={{ padding: "0.45rem 0.75rem" }}>{c.finding_count}</td>
                    <td style={{ padding: "0.45rem 0.75rem", color: riskColor(c.max_risk_score) }}>
                      {c.max_risk_score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <footer style={{ opacity: 0.5, marginTop: "3rem", fontSize: "0.8rem" }}>
        Synthetic demo data. Backend: {API_BASE}
      </footer>
    </main>
  );
}

function Kpi({ label, value, color }: { label: string; value: number; color?: string }) {
  return (
    <div style={card}>
      <div style={{ opacity: 0.65, fontSize: "0.8rem" }}>{label}</div>
      <div style={{ fontSize: "1.8rem", fontWeight: 700, color: color || "#e6e9f2" }}>
        {value}
      </div>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th style={{ padding: "0.6rem 0.75rem", fontWeight: 600, fontSize: "0.78rem", opacity: 0.7 }}>
      {children}
    </th>
  );
}
