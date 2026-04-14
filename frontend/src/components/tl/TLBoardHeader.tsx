export default function TLBoardHeader() {
  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
      <h1 style={{ margin: 0 }}>TL Board</h1>
      <div style={{ fontSize: 12, opacity: 0.8 }}>read‑only • backend stable signals</div>
    </header>
  );
}

