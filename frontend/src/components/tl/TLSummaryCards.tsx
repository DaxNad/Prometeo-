import type { TLMachineLoadItem } from "../../types/tl";

export default function TLSummaryCards({ load }: { load: TLMachineLoadItem[] }) {
  const totalOrders = (load || []).reduce((a, b) => a + Number(b.orders_total || 0), 0);
  const stations = (load || []).length;
  const events = (load || []).reduce((a, b) => a + Number(b.open_events_total || 0), 0);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
      <Card title="ordini totali" value={String(totalOrders)} />
      <Card title="stazioni" value={String(stations)} />
      <Card title="eventi aperti" value={String(events)} />
    </div>
  );
}

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div style={{ background: "#111", border: "1px solid #222", borderRadius: 8, padding: 12 }}>
      <div style={{ fontSize: 12, opacity: 0.8 }}>{title}</div>
      <div style={{ fontSize: 22 }}>{value}</div>
    </div>
  );
}

