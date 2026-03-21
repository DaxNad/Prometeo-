// API minimale: carica JSON locale
async function loadEventsStatic() {
  const res = await fetch("./data/events.latest.json", { cache: "no-store" });
  if (!res.ok) throw new Error("HTTP " + res.status);
  const data = await res.json();
  if (!Array.isArray(data)) throw new Error("JSON non è una lista");
  return data;
}
