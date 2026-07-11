import { useEffect, useState } from "react";
import ProductionDashboard from "./pages/ProductionDashboard";
import TLBoardPage from "./pages/TLBoardPage";
import TLChatPage from "./pages/TLChatPage";
import ArticleSpecificationAcquisitionPage from "./pages/ArticleSpecificationAcquisitionPage";

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
    <div style={{ minHeight: "100vh", background: "#050505", color: "#fff" }}>
      <nav
        aria-label="Navigazione PROMETEO"
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          padding: "10px 16px",
          borderBottom: "1px solid #18181b",
          color: "#9ca3af",
          fontSize: 14,
        }}
      >
        <a
          href="/"
          onClick={(e) => {
            e.preventDefault();
            nav("/");
          }}
          style={{ color: path === "/" ? "#fff" : "#9ca3af", textDecoration: "none", fontWeight: 700 }}
        >
          Chat
        </a>
        <a
          href="/tl-board"
          onClick={(e) => {
            e.preventDefault();
            nav("/tl-board");
          }}
          style={{ color: path === "/tl-board" ? "#fff" : "#9ca3af", textDecoration: "none" }}
        >
          TL Board
        </a>
        <a
          href="/dashboard"
          onClick={(e) => {
            e.preventDefault();
            nav("/dashboard");
          }}
          style={{ color: path === "/dashboard" ? "#fff" : "#9ca3af", textDecoration: "none" }}
        >
          Dashboard
        </a>
        <a
          href="/article-specification/acquire"
          onClick={(e) => {
            e.preventDefault();
            nav("/article-specification/acquire");
          }}
          style={{
            color: path === "/article-specification/acquire" ? "#fff" : "#9ca3af",
            textDecoration: "none",
          }}
        >
          Acquisisci specifica
        </a>
      </nav>

      {path === "/tl-board" ? (
        <TLBoardPage />
      ) : path === "/dashboard" ? (
        <ProductionDashboard />
      ) : path === "/article-specification/acquire" ? (
        <ArticleSpecificationAcquisitionPage />
      ) : (
        <TLChatPage />
      )}
    </div>
  );
}
