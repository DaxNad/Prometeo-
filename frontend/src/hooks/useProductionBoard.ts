import { useEffect, useState } from "react";
import {
  type AgentRuntimeOperationalSummary,
  type MachineLoadResponse,
  getAgentRuntimeOperationalSummary,
  getProductionMachineLoad,
  getProductionSequence,
  getProductionTurnPlan,
} from "../lib/api/prometeo";

type DashboardState = {
  board: unknown;
  delays: unknown;
  load: unknown;
  machineLoad: MachineLoadResponse | null;
  sequence: unknown;
  turnPlan: unknown;
  agentRuntimeOperational: AgentRuntimeOperationalSummary | null;
};

export function useProductionBoard() {
  const [data, setData] = useState<DashboardState>({
    board: {
      warning: "endpoint /production/board non allineato su questo backend",
    },
    delays: {
      warning: "endpoint /production/delays non allineato su questo backend",
    },
    load: {
      warning: "endpoint /production/load non allineato su questo backend",
    },
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

    const nextData: DashboardState = {
      board: {
        warning: "endpoint /production/board non allineato su questo backend",
      },
      delays: {
        warning: "endpoint /production/delays non allineato su questo backend",
      },
      load: {
        warning: "endpoint /production/load non allineato su questo backend",
      },
      machineLoad: null,
      sequence: null,
      turnPlan: null,
      agentRuntimeOperational: null,
    };

    try {
      nextData.machineLoad = await getProductionMachineLoad();
    } catch (err) {
      nextData.machineLoad = {
        ok: false,
        items: [],
        warnings: [
          err instanceof Error ? err.message : "machine-load non disponibile",
        ],
      } as MachineLoadResponse;
    }

    try {
      nextData.sequence = await getProductionSequence();
    } catch (err) {
      nextData.sequence = {
        warning:
          err instanceof Error ? err.message : "sequence non disponibile",
      };
    }

    try {
      nextData.turnPlan = await getProductionTurnPlan();
    } catch (err) {
      nextData.turnPlan = {
        warning:
          err instanceof Error ? err.message : "turn-plan non disponibile",
      };
    }

    try {
      nextData.agentRuntimeOperational =
        await getAgentRuntimeOperationalSummary("ZAW-1");
    } catch (err) {
      nextData.agentRuntimeOperational = {
        line_id: "ZAW-1",
        orders_total: 0,
        orders_monitor: 0,
        orders_investigate: 0,
        orders_ok: 0,
        orders_blocked: 0,
        orders_overdue: 0,
        orders_urgent: 0,
        legacy_bootstrap_count: 0,
        domain_order_count: 0,
      };
    }

    setData(nextData);
    setLoading(false);
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
