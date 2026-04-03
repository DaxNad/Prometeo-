import { useEffect, useState } from "react";
import {
  getAgentRuntimeOperationalSummary,
  getProductionBoard,
  getProductionDelays,
  getProductionLoad,
  getProductionMachineLoad,
  getProductionSequence,
  getProductionTurnPlan,
} from "../lib/api/prometeo";

type DashboardState = {
  board: unknown;
  delays: unknown;
  load: unknown;
  machineLoad: unknown;
  sequence: unknown;
  turnPlan: unknown;
  agentRuntimeOperational: unknown;
};

export function useProductionBoard() {
  const [data, setData] = useState<DashboardState>({
    board: null,
    delays: null,
    load: null,
    machineLoad: null,
    sequence: null,
    turnPlan: null,
    agentRuntimeOperational: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAll() {
    setLoading(true);
    setError(null);

    try {
      const [
        board,
        delays,
        load,
        machineLoad,
        sequence,
        agentRuntimeOperational,
      ] = await Promise.all([
        getProductionBoard(),
        getProductionDelays(),
        getProductionLoad(),
        getProductionMachineLoad(),
        getProductionSequence(),
        getAgentRuntimeOperationalSummary("LINEA_A"),
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
        machineLoad,
        sequence,
        turnPlan,
        agentRuntimeOperational,
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
