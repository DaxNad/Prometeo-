import { useCallback, useEffect, useRef, useState } from "react";
import {
  type MachineLoadResponse,
  getProductionBoardState,
  getProductionMachineLoad,
} from "../lib/api/prometeo";
import type { BoardItem } from "../types/production";

const AUTO_REFRESH_MS = 30_000;

type DashboardState = {
  boardItems: BoardItem[];
  machineLoad: MachineLoadResponse | null;
  lastUpdated: Date | null;
};

const EMPTY: DashboardState = {
  boardItems: [],
  machineLoad: null,
  lastUpdated: null,
};

export function useProductionBoard() {
  const [data, setData] = useState<DashboardState>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const loadedOnce = useRef(false);

  const loadAll = useCallback(async () => {
    if (!loadedOnce.current) setLoading(true);
    setError(null);

    const next: DashboardState = { ...EMPTY, lastUpdated: new Date() };

    await Promise.allSettled([
      getProductionBoardState().then((r) => {
        next.boardItems = r.items ?? [];
      }),
      getProductionMachineLoad().then((r) => {
        next.machineLoad = r;
      }),
    ]);

    setData(next);
    setLoading(false);
    loadedOnce.current = true;
  }, []);

  useEffect(() => {
    void loadAll();
    const timer = setInterval(() => void loadAll(), AUTO_REFRESH_MS);
    return () => clearInterval(timer);
  }, [loadAll]);

  return { data, loading, error, reload: loadAll };
}
