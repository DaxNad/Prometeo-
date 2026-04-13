
export function normalizeStationName(raw: string): string {
  return raw
    .replace("_", "-")
    .replace("LINEA1", "LINEA-1")
    .replace("LINEA_A", "LINEA-A")
    .toUpperCase();
}

export function dedupeByArticle(items: any[]) {
  const map = new Map();

  for (const item of items) {
    const key = item.article + "::" + item.critical_station;

    if (!map.has(key)) {
      map.set(key, { ...item });
    } else {
      const prev = map.get(key);
      prev.quantity += item.quantity;
    }
  }

  return Array.from(map.values());
}

