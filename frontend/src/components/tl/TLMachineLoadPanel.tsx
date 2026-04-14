import type { TLMachineLoadItem } from "../../types/tl";

export default function TLMachineLoadPanel({ items }: { items: TLMachineLoadItem[] }) {
  const max = Math.max(1, ...items.map((i) => Number(i.orders_total || 0)));
  return (
    <section style={{ background: "#111", border: "1px solid #222", borderRadius: 8, padding: 12 }}>
      <strong style={{ display: "block", marginBottom: 8 }}>carico postazioni</strong>
      {items.map((m) => {
        const pct = Math.round((Number(m.orders_total || 0) / max) * 100);
        return (
          <div key={m.station} style={{ marginBottom: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
              <span>{m.station}</span>
              <span>{m.orders_total}</span>
            </div>
            <div style={{ height: 10, background: "#222", borderRadius: 6, overflow: "hidden" }}>
              <div style={{ width: `${pct}%`, height: "100%", background: "#2563eb" }} />
            </div>
          </div>
        );
      })}
      {items.length === 0 && <div style={{ opacity: 0.7 }}>nessun dato</div>}
    </section>
  );
}

