import { useMemo } from "react";
import type { TLSequenceItem } from "../../types/tl";
import { PriorityBadge, RiskBadge } from "./TLBadges";

interface Props {
  items: TLSequenceItem[];
  onSelect: (it: TLSequenceItem) => void;
  filters: { station: string; risk: string; onlyEvent: boolean; onlyBlocked: boolean; query: string };
}

export default function TLSequenceTable({ items, onSelect, filters }: Props) {
  const rows = useMemo(() => {
    return (items || [])
      .filter((i) => (filters.station === "ALL" ? true : i.critical_station === filters.station))
      .filter((i) => (filters.onlyEvent ? Boolean(i.event_impact) : true))
      .filter((i) => (filters.onlyBlocked ? String(i.customer_priority || "").toUpperCase() === "ALTA" : true))
      .filter((i) => {
        const q = filters.query.trim().toLowerCase();
        if (!q) return true;
        return String(i.article || i.order_id || "").toLowerCase().includes(q);
      });
  }, [items, filters]);

  const stations = Array.from(new Set((items || []).map((i) => i.critical_station).filter(Boolean))) as string[];

  return (
    <div>
      <table style={{ width: "100%", borderCollapse: "collapse", background: "#111", border: "1px solid #222" }}>
        <thead>
          <tr style={{ background: "#0b1220" }}>
            <th style={{ textAlign: "right", padding: 8 }}>Rank</th>
            <th style={{ textAlign: "left", padding: 8 }}>Articolo/Ordine</th>
            <th style={{ textAlign: "left", padding: 8 }}>Postazione critica</th>
            <th style={{ textAlign: "left", padding: 8 }}>Priorità</th>
            <th style={{ textAlign: "left", padding: 8 }}>Eventi</th>
            <th style={{ textAlign: "left", padding: 8 }}>Rischio</th>
            <th style={{ textAlign: "left", padding: 8 }}>Motivo priorità</th>
            <th style={{ textAlign: "left", padding: 8 }}>Azione suggerita</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={(r.order_id || r.article || idx) + "-row"} style={{ borderTop: "1px solid #222", cursor: "pointer" }} onClick={() => onSelect(r)}>
              <td style={{ padding: 8, textAlign: "right" }}>{r.rank ?? idx + 1}</td>
              <td style={{ padding: 8 }}><strong>{r.article || r.order_id}</strong></td>
              <td style={{ padding: 8 }}>{r.critical_station}</td>
              <td style={{ padding: 8 }}><PriorityBadge value={r.customer_priority} /></td>
              <td style={{ padding: 8 }}>{r.event_impact ? "Sì" : "No"}</td>
              <td style={{ padding: 8 }}><RiskBadge level={(r as any).risk_level} /></td>
              <td style={{ padding: 8 }}>{(r as any).priority_reason || ""}</td>
              <td style={{ padding: 8 }}>{(r as any).suggested_action || ""}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan={8} style={{ padding: 12, opacity: 0.7 }}>nessun elemento</td>
            </tr>
          )}
        </tbody>
      </table>

      <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
        stazioni disponibili: {stations.length > 0 ? stations.join(", ") : "-"}
      </div>
    </div>
  );
}
