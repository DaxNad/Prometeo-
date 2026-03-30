const API_BASE =
  import.meta.env.VITE_PROMETEO_API_BASE?.replace(/\/+$/, "") ||
  "https://prometeo-production-3855.up.railway.app";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }

  return res.json() as Promise<T>;
}

export async function getProductionBoard<T = unknown>() {
  return apiGet<T>("/production/board");
}

export async function getProductionDelays<T = unknown>() {
  return apiGet<T>("/production/delays");
}

export async function getProductionLoad<T = unknown>() {
  return apiGet<T>("/production/load");
}

export async function getProductionSequence<T = unknown>() {
  return apiGet<T>("/production/sequence");
}

export async function getProductionTurnPlan<T = unknown>() {
  return apiGet<T>("/production/turn-plan");
}
