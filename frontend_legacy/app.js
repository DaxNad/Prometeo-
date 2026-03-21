const STORAGE_KEY = "prometeo_ordini";

async function loadData() {
  let data = localStorage.getItem(STORAGE_KEY);

  if (data) {
    return JSON.parse(data);
  }

  const res = await fetch("./ordini.json");
  const json = await res.json();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(json));
  return json;
}

function saveData(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function color(stato) {
  if (stato === "critico") return "red";
  if (stato === "attenzione") return "orange";
  return "green";
}

function renderDashboard(data) {
  const app = document.getElementById("app");
  app.innerHTML = "";

  data.sort((a, b) => a.priorita - b.priorita);

  data.forEach((ordine, index) => {
    const div = document.createElement("div");
    div.style.background = color(ordine.stato);
    div.style.color = "white";
    div.style.padding = "12px";
    div.style.margin = "6px";
    div.style.borderRadius = "8px";
    div.innerText = `${ordine.codice} — ${ordine.descrizione}`;

    div.onclick = () => openEditor(index);

    app.appendChild(div);
  });
}

function openEditor(index) {
  const data = JSON.parse(localStorage.getItem(STORAGE_KEY));
  const o = data[index];

  const app = document.getElementById("app");

  app.innerHTML = `
    <h2>${o.codice}</h2>

    Descrizione:<br>
    <input id="desc" value="${o.descrizione}"><br>

    Stato:<br>
    <select id="stato">
      <option value="critico">critico</option>
      <option value="attenzione">attenzione</option>
      <option value="ok">ok</option>
    </select><br>

    Priorità:<br>
    <input id="prio" type="number" value="${o.priorita}"><br>

    Componenti:<br>
    <input id="comp" value="${o.componenti || ""}"><br>

    Note:<br>
    <textarea id="note">${o.note || ""}</textarea><br>

    Turno:<br>
    <input id="turno" value="${o.turno || ""}"><br><br>

    <button id="save">Salva</button>
    <button id="back">Indietro</button>
  `;

  document.getElementById("stato").value = o.stato;

  document.getElementById("save").onclick = () => {
    o.descrizione = document.getElementById("desc").value;
    o.stato = document.getElementById("stato").value;
    o.priorita = parseInt(document.getElementById("prio").value);
    o.componenti = document.getElementById("comp").value;
    o.note = document.getElementById("note").value;
    o.turno = document.getElementById("turno").value;

    saveData(data);
    renderDashboard(data);
  };

  document.getElementById("back").onclick = () => {
    renderDashboard(data);
  };
}

loadData().then(renderDashboard);
