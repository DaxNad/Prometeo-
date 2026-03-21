function $(id) { 
  return document.getElementById(id); 
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderEventItem(e) {
  const note = e?.payload?.note ? escapeHtml(e.payload.note) : "";

  return `
    <li class="item">
      <div class="row1">
        <div>${escapeHtml(e.ts || "")}</div>
        <div class="badge">${escapeHtml(e.type || "")}</div>
      </div>
      <div class="row2">
        ${escapeHtml(e.postazione || "—")} · P${String(e.priorita ?? "—")}
      </div>
      ${note ? `<div class="note">${note}</div>` : ``}
    </li>
  `;
}

async function reload() {
  const status = $("status");
  const list = $("eventList");

  status.textContent = "Caricamento…";

  try {
    const events = await loadEventsStatic();

    events.sort((a, b) =>
      String(b.ts || "").localeCompare(String(a.ts || ""))
    );

    list.innerHTML = events.map(renderEventItem).join("");
    status.textContent = `OK: ${events.length} eventi.`;
  } catch (err) {
    status.textContent = "Errore: " + (err?.message || String(err));
  }
}

/* ===== AUTO REFRESH ===== */

const AUTO_REFRESH_MS = 10000; // 10 secondi

function startAutoRefresh() {
  setInterval(() => {
    reload();
  }, AUTO_REFRESH_MS);
}

document.addEventListener("DOMContentLoaded", () => {
  $("btnReload").addEventListener("click", reload);

  reload();           // primo caricamento
  startAutoRefresh(); // attiva auto refresh
});
