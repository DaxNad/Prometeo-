export default function TLBoardHeader() {
  const isDemo = String((import.meta as any)?.env?.VITE_DEMO || "").toLowerCase() === "true"
    || String((import.meta as any)?.env?.VITE_PROMETEO_MODE || "").toLowerCase() === "demo";
  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
      <h1 style={{ margin: 0 }}>TL Board</h1>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <span style={{ fontSize: 12, opacity: 0.9 }}>{isDemo ? "DEMO" : "LIVE"}</span>
        <span style={{ fontSize: 12, opacity: 0.8 }}>read‑only • backend stable signals</span>
      </div>
    </header>
  );
}
