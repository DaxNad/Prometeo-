import type { TLSequenceItem, TLExplainItem } from "../../types/tl";
import { TLSignals } from "./TLSignals";
import { PriorityBadge, RiskBadge } from "./TLBadges";

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
  const groups = groupReasons(x?.reasons || []);

  return (
    <aside style={{ background: "#111", border: "1px solid #222", borderRadius: 8, padding: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <strong>dettaglio</strong>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <RiskBadge level={x?.risk_level || (item as any).risk_level} />
          <PriorityBadge value={item.customer_priority} />
        </div>
      </div>
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
        <strong>segnali</strong>
        <TLSignals reasons={x?.reasons} eventImpact={Boolean(item.event_impact)} />
      </div>

      <ExplainGroups groups={groups} />
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

function ExplainGroups({ groups }: { groups: Record<string, string[]> }) {
  const order = [
    "Eventi operativi",
    "Pressioni condivise",
    "Saturazione postazione",
    "Vincoli di sequenza",
    "Altre note",
  ];
  const nonEmpty = order.filter((k) => (groups[k] || []).length > 0);
  if (nonEmpty.length === 0) {
    return (
      <div style={{ marginTop: 8 }}>
        <strong>explain</strong>
        <div style={{ opacity: 0.7 }}>non disponibile</div>
      </div>
    );
  }
  return (
    <div style={{ marginTop: 8, display: "grid", gap: 8 }}>
      {nonEmpty.map((k) => (
        <section key={k} style={{ background: "#0e0e0e", border: "1px solid #1f2937", borderRadius: 8, padding: 8 }}>
          <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{k}</div>
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {groups[k].map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}

function groupReasons(reasons: string[]): Record<string, string[]> {
  const g: Record<string, string[]> = {
    "Eventi operativi": [],
    "Pressioni condivise": [],
    "Saturazione postazione": [],
    "Vincoli di sequenza": [],
    "Altre note": [],
  };
  for (const r of reasons) {
    const t = r.toLowerCase();
    if (/event|operat/.test(t)) g["Eventi operativi"].push(r);
    else if (/shared|condivis|component/.test(t)) g["Pressioni condivise"].push(r);
    else if (/saturaz|overload|coda/.test(t)) g["Saturazione postazione"].push(r);
    else if (/preceden|sequence|vincolo/.test(t)) g["Vincoli di sequenza"].push(r);
    else g["Altre note"].push(r);
  }
  return g;
}
