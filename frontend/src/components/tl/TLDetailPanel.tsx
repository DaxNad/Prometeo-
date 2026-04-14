import type { TLSequenceItem, TLExplainItem } from "../../types/tl";

interface Props {
  item?: TLSequenceItem | null;
  explain?: TLExplainItem[];
}

export default function TLDetailPanel({ item, explain }: Props) {
  if (!item) return (
    <aside style={{ background: "#111", border: "1px solid #222", borderRadius: 8, padding: 12 }}>
      <div style={{ opacity: 0.7 }}>seleziona una riga per i dettagli</div>
    </aside>
  );

  const x = (explain || []).find((e) => e.order_id === item.order_id || e.article === item.article);

  return (
    <aside style={{ background: "#111", border: "1px solid #222", borderRadius: 8, padding: 12 }}>
      <strong style={{ display: "block", marginBottom: 8 }}>dettaglio</strong>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        <Field k="identità" v={String(item.article || item.order_id || "-")} />
        <Field k="critical station" v={String(item.critical_station || "-")} />
        <Field k="priority" v={String(item.customer_priority || "-")} />
        <Field k="event impact" v={String(item.event_impact ? "YES" : "NO")} />
        <Field k="risk level" v={String(x?.risk_level || (item as any).risk_level || "-")} />
        <Field k="priority reason" v={String(x?.priority_reason || (item as any).priority_reason || "")} />
        <Field k="suggested action" v={String(x?.suggested_action || (item as any).suggested_action || "")} />
      </div>

      <div style={{ marginTop: 8 }}>
        <strong>explain</strong>
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {(x?.reasons || []).map((r, i) => (
            <li key={i}>{r}</li>
          ))}
          {(x?.reasons || []).length === 0 && <li style={{ opacity: 0.7 }}>non disponibile</li>}
        </ul>
      </div>
    </aside>
  );
}

function Field({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <div style={{ fontSize: 12, opacity: 0.7 }}>{k}</div>
      <div>{v}</div>
    </div>
  );
}

