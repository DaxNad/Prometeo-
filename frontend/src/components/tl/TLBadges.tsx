export function RiskBadge({ level }: { level?: string }) {
  const v = String(level || "LOW").toUpperCase();
  const clr: Record<string, string> = { LOW: "#1f5f3a", MEDIUM: "#7c5a10", HIGH: "#7f1d1d" };
  return (
    <span style={{ background: clr[v] || "#333", color: "#fff", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}>
      {v}
    </span>
  );
}

export function PriorityBadge({ value }: { value?: string }) {
  const v = String(value || "").toUpperCase();
  const clr: Record<string, string> = { ALTA: "#7f1d1d", MEDIA: "#7c5a10", BASSA: "#1f5f3a" };
  return (
    <span style={{ background: clr[v] || "#333", color: "#fff", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}>{v || "NEUTRO"}</span>
  );
}

