import { useEffect, useState } from "react";
import {
  getProductionBoard,
  getProductionDelays,
  getProductionLoad,
  getProductionSequence,
  getProductionTurnPlan,
} from "../lib/api/prometeo";

type DashboardState = {
  board: unknown;
  delays: unknown;
  load: unknown;
  sequence: unknown;
  turnPlan: unknown;
};

export function useProductionBoard() {
  const [data, setData] = useState<DashboardState>({
    board: null,
    delays: null,
    load: null,
    sequence: null,
    turnPlan: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAll() {
    setLoading(true);
    setError(null);

    try {
      const [board, delays, load, sequence] = await Promise.all([
        getProductionBoard(),
        getProductionDelays(),
        getProductionLoad(),
        getProductionSequence(),
      ]);

      let turnPlan: unknown = null;

      try {
        turnPlan = await getProductionTurnPlan();
      } catch (err) {
        console.warn("turn-plan non disponibile:", err);
      }

      setData({
        board,
        delays,
        load,
        sequence,
        turnPlan,
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Errore caricamento dashboard";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, []);

  return {
    data,
    loading,
    error,
    reload: loadAll,
  };
}
