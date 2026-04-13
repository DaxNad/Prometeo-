import { useEffect, useState } from "react";

import {
  getProductionMachineLoad,
  getProductionSequence,
  getProductionTurnPlan,
  getAgentRuntimeOperationalSummary,
} from "../lib/api/prometeo";

import {
  normalizeStationName,
  dedupeByArticle,
} from "../services/normalize";

type GenericItem = Record<string, unknown>;

type SequenceApiResponse = {
  items?: GenericItem[];
};

type MachineLoadApiResponse = {
  items?: GenericItem[];
};

export function useProductionBoard() {
  const [data, setData] = useState<any>(null);

  async function loadAll() {
    const machineLoadUnknown = await getProductionMachineLoad();
    const sequenceUnknown = await getProductionSequence();
    const turnPlan = await getProductionTurnPlan();
    const summary = await getAgentRuntimeOperationalSummary("ZAW-1");

    const machineLoad = machineLoadUnknown as MachineLoadApiResponse;
    const sequenceRaw = sequenceUnknown as SequenceApiResponse;

    const sequence = dedupeByArticle(
      (sequenceRaw.items ?? []).map((i: GenericItem) => ({
        ...i,
        critical_station: normalizeStationName(String(i.critical_station ?? "")),
      })),
    );

    const load = (machineLoad.items ?? []).map((i: GenericItem) => ({
      ...i,
      station: normalizeStationName(String(i.station ?? "")),
    }));

    setData({
      sequence,
      load,
      turnPlan,
      summary,
    });
  }

  useEffect(() => {
    void loadAll();
  }, []);

  return data;
}
