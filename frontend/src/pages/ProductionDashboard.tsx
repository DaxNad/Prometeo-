import { useProductionBoard } from "../hooks/useProductionBoard";

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

function RuntimeSummaryCard({ value }: { value: any }) {
  if (!value) {
    return (
      <section style={{ border: "1px solid #333", padding: 16, borderRadius: 12 }}>
        <h2 style={{ marginTop: 0 }}>Agent Runtime Summary</h2>
        <p style={{ margin: 0 }}>Nessun dato disponibile.</p>
      </section>
    );
  }

  return (
    <section style={{ border: "1px solid #333", padding: 16, borderRadius: 12 }}>
      <h2 style={{ marginTop: 0 }}>Agent Runtime Summary</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>
        <div><strong>Linea</strong><div>{value.line_id ?? "-"}</div></div>
        <div><strong>Ordini totali</strong><div>{value.orders_total}</div></div>
        <div><strong>Ordini OK</strong><div>{value.orders_ok}</div></div>

        <div><strong>Monitor</strong><div>{value.orders_monitor}</div></div>
        <div><strong>Investigate</strong><div>{value.orders_investigate}</div></div>
        <div><strong>Bloccati</strong><div>{value.orders_blocked}</div></div>

        <div><strong>Scaduti</strong><div>{value.orders_overdue}</div></div>
        <div><strong>Urgenti</strong><div>{value.orders_urgent}</div></div>
        <div><strong>Domain order</strong><div>{value.domain_order_count}</div></div>

        <div><strong>Legacy bootstrap</strong><div>{value.legacy_bootstrap_count}</div></div>
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
        value={data.turnPlan ?? { warning: "endpoint /production/turn-plan attualmente non disponibile" }}
      />
    </main>
  );
}
