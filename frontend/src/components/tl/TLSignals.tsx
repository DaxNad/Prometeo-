export function TLSignals({ reasons, eventImpact }: { reasons?: string[]; eventImpact?: boolean }) {
  const labels = classifySignals(reasons || [], !!eventImpact);
  if (labels.length === 0) return null;
  return (
    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
      {labels.map((l, i) => (
        <span
          key={i}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            background: "#1a1a1a",
            border: "1px solid #333",
            borderRadius: 999,
            padding: "2px 8px",
            fontSize: 11,
            color: "#e5e7eb",
          }}
        >
          <span aria-hidden style={{ width: 6, height: 6, borderRadius: 999, background: signalColor(l) }} />
          <span>{l}</span>
        </span>
      ))}
    </div>
  );
}

function signalColor(label: string): string {
  const map: Record<string, string> = {
    "postazione satura": "#f59e0b",
    "evento cliente aperto": "#ef4444",
    "componente condiviso in conflitto": "#f97316",
    "vincolo sequenza": "#60a5fa",
  };
  return map[label] || "#6b7280";
}

export function classifySignals(reasons: string[], eventImpact: boolean): string[] {
  const labels: string[] = [];
  const txt = reasons.join(" | ").toLowerCase();
  if (eventImpact) labels.push("evento cliente aperto");
  if (/(saturaz|saturated|overload)/.test(txt)) labels.push("postazione satura");
  if (/(shared|condivis|component)/.test(txt)) labels.push("componente condiviso in conflitto");
  if (/(preceden|sequence|vincolo)/.test(txt)) labels.push("vincolo sequenza");
  // de-dup
  return Array.from(new Set(labels));
}

