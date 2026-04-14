import ProductionDashboard from "./pages/ProductionDashboard";
import TLBoardPage from "./pages/TLBoardPage";

export default function App() {
  // Temporarily expose TLBoard below the existing dashboard (read-only)
  return (
    <div style={{ display: "grid", gap: 24 }}>
      <ProductionDashboard />
      <TLBoardPage />
    </div>
  );
}
