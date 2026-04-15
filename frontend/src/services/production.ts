const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

async function fetchJson(path: string) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Errore API ${response.status} su ${path}`);
  }

  return response.json();
}

export async function fetchProductionBoard() {
  return fetchJson("/production/board-state");
}

export async function fetchProductionLoad() {
  return fetchJson("/production/machine-load");
}

export async function fetchProductionSequence() {
  return fetchJson("/production/sequence");
}

export async function fetchProductionSequenceAtlasMerge() {
  return fetchJson("/production/sequence/atlas-merge");
}

export async function fetchProductionTurnPlan() {
  return fetchJson("/production/turn-plan");
}
