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
