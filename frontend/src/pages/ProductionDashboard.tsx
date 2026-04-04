import { useProductionBoard } from "../hooks/useProductionBoard";
import type { AgentRuntimeOperationalSummary } from "../lib/api/prometeo";

function Block({ title, value }: { title: string; value: unknown }) {
  return (
    <section style={{ border: "1px solid #333", padding: 16, borderRadius: 12 }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>
        {JSON.stringify(value, null, 2)}
      </pre>
    </section>
  );
}

function getRuntimeTone(value: AgentRuntimeOperationalSummary) {
  if (value.orders_blocked > 0 || value.orders_overdue > 0) {
    return {
      borderColor: "#7f1d1d",
      background: "#2a1111",
      label: "CRITICO",
    };
  }

  if (value.orders_investigate > 0 || value.orders_urgent > 0) {
    return {
      borderColor: "#7c5a10",
      background: "#2a2210",
      label: "ATTENZIONE",
    };
  }

  return {
    borderColor: "#1f5f3a",
    background: "#11261a",
    label: "STABILE",
  };
}

function MetricCard({
  label,
  value,
}: {
  label: string;
  value: number | string | null;
}) {
  return (
    <div
      style={{
        border: "1px solid #333",
        borderRadius: 10,
        padding: 12,
        background: "#111",
      }}
    >
      <div style={{ fontSize: 12, opacity: 0.75 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, marginTop: 6 }}>{value ?? "-"}</div>
    </div>
  );
}

function RuntimeSummaryCard({
  value,
}: {
  value: AgentRuntimeOperationalSummary | null;
}) {
  if (!value) {
    return (
      <section style={{ border: "1px solid #333", padding: 16, borderRadius: 12 }}>
        <h2 style={{ marginTop: 0 }}>Agent Runtime</h2>
        <p style={{ margin: 0 }}>Nessun dato disponibile.</p>
      </section>
    );
  }

  const tone = getRuntimeTone(value);

  return (
    <section
      style={{
        border: `1px solid ${tone.borderColor}`,
        background: tone.background,
        padding: 16,
        borderRadius: 12,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 12,
          marginBottom: 16,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2 style={{ margin: 0 }}>Agent Runtime — Sintesi Operativa</h2>
          <div style={{ marginTop: 6, opacity: 0.8 }}>
            Linea: <strong>{value.line_id ?? "globale"}</strong>
          </div>
        </div>

        <div
          style={{
            border: `1px solid ${tone.borderColor}`,
            borderRadius: 999,
            padding: "6px 10px",
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          {tone.label}
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: 12,
        }}
      >
        <MetricCard label="Ordini totali" value={value.orders_total} />
        <MetricCard label="Da investigare" value={value.orders_investigate} />
        <MetricCard label="Ordini bloccati" value={value.orders_blocked} />
        <MetricCard label="Ordini scaduti" value={value.orders_overdue} />
        <MetricCard label="Ordini urgenti" value={value.orders_urgent} />
        <MetricCard label="Ordini OK" value={value.orders_ok} />
        <MetricCard label="Monitor" value={value.orders_monitor} />
        <MetricCard label="Domain order" value={value.domain_order_count} />
        <MetricCard label="Legacy bootstrap" value={value.legacy_bootstrap_count} />
      </div>
    </section>
  );
}

export default function ProductionDashboard() {
  const { data, loading, error, reload } = useProductionBoard();

  if (loading) return <div>Caricamento dashboard produzione...</div>;

  if (error) {
    return (
      <div style={{ padding: 16 }}>
        <p>Errore: {error}</p>
        <button onClick={() => void reload()}>Riprova</button>
      </div>
    );
  }

  return (
    <main style={{ display: "grid", gap: 16, padding: 16 }}>
      <h1 style={{ marginBottom: 0 }}>PROMETEO — TL Board</h1>

      <RuntimeSummaryCard value={data.agentRuntimeOperational} />

      <Block title="Machine Load" value={data.machineLoad} />
      <Block title="Production Board" value={data.board} />
      <Block title="Production Delays" value={data.delays} />
      <Block title="Production Load" value={data.load} />
      <Block title="Production Sequence" value={data.sequence} />
      <Block
        title="Production Turn Plan"
        value={
          data.turnPlan ?? {
            warning: "endpoint /production/turn-plan attualmente non disponibile",
          }
        }
      />
    </main>
  );
}
