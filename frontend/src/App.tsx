import { useEffect, useState } from "react";
import ProductionDashboard from "./pages/ProductionDashboard";
import TLBoardPage from "./pages/TLBoardPage";
import TLChatPage from "./pages/TLChatPage";

export default function App() {
  const [path, setPath] = useState<string>(typeof window !== "undefined" ? window.location.pathname : "/");

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname || "/");
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  function nav(to: string) {
    if (to === path) return;
    window.history.pushState({}, "", to);
    setPath(to);
  }

  return (
    <div style={{ padding: 12 }}>
      <nav style={{ display: "flex", gap: 12, marginBottom: 12 }}>
        <a href="/" onClick={(e) => { e.preventDefault(); nav("/"); }} style={{ color: path === "/" ? "#fff" : "#9ca3af" }}>TL Chat</a>
        <a href="/tl-board" onClick={(e) => { e.preventDefault(); nav("/tl-board"); }} style={{ color: path === "/tl-board" ? "#fff" : "#9ca3af" }}>TL Board</a>
        <a href="/dashboard" onClick={(e) => { e.preventDefault(); nav("/dashboard"); }} style={{ color: path === "/dashboard" ? "#fff" : "#9ca3af" }}>Dashboard</a>
      </nav>
      {path === "/tl-board" ? <TLBoardPage /> : path === "/dashboard" ? <ProductionDashboard /> : <TLChatPage />}
    </div>
  );
}
