const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ??
  import.meta.env.VITE_PROMETEO_API_BASE ??
  "https://prometeo-railway-bootstrap-production.up.railway.app"
).replace(/\/+$/, "");

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
  return fetchJson("/production/board");
}

export async function fetchProductionLoad() {
  return fetchJson("/production/machine-load");
}

export async function fetchProductionSequence() {
  return fetchJson("/production/sequence");
}

export async function fetchProductionTurnPlan() {
  return fetchJson("/production/turn-plan");
}
