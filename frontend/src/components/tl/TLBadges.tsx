export function RiskBadge({ level }: { level?: string }) {
  const v = String(level || "LOW").toUpperCase();
  const clr: Record<string, string> = { LOW: "#1f5f3a", MEDIUM: "#7c5a10", HIGH: "#7f1d1d" };
  const short: Record<string, string> = { LOW: "L", MEDIUM: "M", HIGH: "H" };
  return (
    <span
      title={v}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        background: "#1a1a1a",
        border: "1px solid #333",
        borderRadius: 999,
        padding: "1px 6px",
        fontSize: 11,
        color: "#e5e7eb",
      }}
    >
      <span aria-hidden style={{ width: 8, height: 8, borderRadius: 999, background: clr[v] || "#555" }} />
      <strong style={{ letterSpacing: 0.3 }}>{short[v] || "-"}</strong>
    </span>
  );
}

export function PriorityBadge({ value }: { value?: string }) {
  const v = String(value || "").toUpperCase();
  const clr: Record<string, string> = { ALTA: "#7f1d1d", MEDIA: "#7c5a10", BASSA: "#1f5f3a" };
  const short: Record<string, string> = { ALTA: "A", MEDIA: "M", BASSA: "B" };
  const label = v || "NEUTRO";
  return (
    <span
      title={label}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        background: "#1a1a1a",
        border: "1px solid #333",
        borderRadius: 999,
        padding: "1px 6px",
        fontSize: 11,
        color: "#e5e7eb",
      }}
    >
      <span aria-hidden style={{ width: 8, height: 8, borderRadius: 999, background: clr[v] || "#555" }} />
      <strong style={{ letterSpacing: 0.3 }}>{short[v] || "-"}</strong>
    </span>
  );
}
