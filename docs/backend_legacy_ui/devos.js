async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${url} -> HTTP ${res.status}`);
  }
  return res.json();
}

function badgeClass(value) {
  const v = String(value || "").toLowerCase().trim().replace(/\s+/g, "-");
  return `badge ${v}`;
}

function setList(el, items) {
  el.innerHTML = "";
  (items || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  });
}

function setChips(el, items) {
  el.innerHTML = "";
  (items || []).forEach((item) => {
    const span = document.createElement("span");
    span.className = "chip";
    span.textContent = item;
    el.appendChild(span);
  });
}

function setModules(tableBody, modules) {
  tableBody.innerHTML = "";
  (modules || []).forEach((m) => {
    const tr = document.createElement("tr");

    const tdModulo = document.createElement("td");
    tdModulo.textContent = m.modulo || "";

    const tdStato = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = badgeClass(m.stato);
    badge.textContent = m.stato || "";
    tdStato.appendChild(badge);

    const tdNote = document.createElement("td");
    tdNote.textContent = m.note || "";

    tr.appendChild(tdModulo);
    tr.appendChild(tdStato);
    tr.appendChild(tdNote);

    tableBody.appendChild(tr);
  });
}

async function loadDevOS() {
  const statusLine = document.getElementById("statusLine");
  statusLine.textContent = "Aggiornamento in corso...";

  try {
    const [status, tasks, logs, milestones] = await Promise.all([
      fetchJson("/dev/status"),
      fetchJson("/dev/tasks"),
      fetchJson("/dev/logs"),
      fetchJson("/dev/milestones"),
    ]);

    setModules(
      document.querySelector("#modulesTable tbody"),
      status.modules || []
    );

    setList(document.getElementById("objectivesList"), status.immediate_objectives || []);
    setList(document.getElementById("blocksList"), status.open_blocks || []);
    setChips(document.getElementById("priorityChips"), status.priority_modules || []);
    setList(document.getElementById("milestonesList"), milestones.milestones || []);

    document.getElementById("tasksRaw").textContent = tasks.raw || "Nessun contenuto";
    document.getElementById("logsRaw").textContent = logs.raw || "Nessun contenuto";
    document.getElementById("statusRaw").textContent = status.raw || "Nessun contenuto";

    statusLine.textContent = "Aggiornato correttamente";
  } catch (err) {
    console.error(err);
    statusLine.textContent = `Errore: ${err.message}`;
  }
}

document.getElementById("refreshBtn").addEventListener("click", loadDevOS);

document.getElementById("toggleRawBtn").addEventListener("click", () => {
  const rawCard = document.getElementById("rawCard");
  rawCard.style.display = rawCard.style.display === "none" ? "block" : "none";
});

loadDevOS();
