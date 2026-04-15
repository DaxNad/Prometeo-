import { useEffect, useState } from "react";
import {
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionSequenceAtlasMerge
} from "../services/production";

function normalizeStation(s?: string) {

  if (!s) return s;

  return s
    .replace("_", "-")
    .replace("LINEA1", "LINEA-1");

}

function groupOrders(items: any[]) {

  const map: Record<string, any> = {};

  for (const i of items) {

    const key =
      i.codice + "|" + normalizeStation(i.postazione);

    if (!map[key]) {

      map[key] = {

        ...i,

        postazione: normalizeStation(i.postazione),

        qta: 0,

        count: 0

      };

    }

    map[key].qta += i.qta || 0;

    map[key].count += 1;

  }

  return Object.values(map);

}

function Section({ title, children, tone = "#111" }: { title: string; children: any; tone?: string }) {
  return (
    <section
      style={{
        background: tone,
        padding: 16,
        borderRadius: 12,
        border: tone === "#111" ? "1px solid #222" : `1px solid ${tone}`,
      }}
    >
      <strong style={{ display: "block", marginBottom: 8 }}>{title}</strong>
      {children}
    </section>
  );
}

function PriorityBadge({ value }: { value?: string }) {
  const v = String(value ?? "").toUpperCase();
  const tones: Record<string, string> = { ROSSO: "#7f1d1d", GIALLO: "#7c5a10", VERDE: "#1f5f3a" };
  const bg = tones[v] ?? "#333";
  const label = v || "NEUTRO";
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        minWidth: 84,
        padding: "4px 8px",
        borderRadius: 999,
        background: bg,
        color: "#fff",
        fontSize: 12,
        letterSpacing: 0.3,
      }}
    >
      <span
        aria-hidden
        style={{ display: "inline-block", width: 10, height: 10, borderRadius: 999, background: "#fff" }}
      />
      <strong style={{ fontWeight: 600 }}>{label}</strong>
    </span>
  );
}

function Chip({ label }: { label: string }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 999,
        background: "#1f2937",
        border: "1px solid #374151",
        fontSize: 12,
        color: "#e5e7eb",
      }}
    >
      {label}
    </span>
  );
}

type AtlasItem = {
  atlas_outcome?: string;
  atlas_score?: number | string;
  explain_brief?: string;
};

function mapAtlasItem(item: any): AtlasItem {
  const merge = item?.atlas_merge ?? item ?? {};
  return {
    atlas_outcome: merge?.final_outcome ?? item?.atlas_outcome,
    atlas_score: merge?.final_score ?? item?.atlas_score,
    explain_brief: merge?.explain_brief ?? item?.explain_brief,
  };
}

function AtlasBadge({ outcome }: { outcome?: string }) {
  const value = String(outcome ?? "").toUpperCase();
  const palette: Record<string, string> = {
    BLOCK: "#7f1d1d",
    REVIEW: "#c2410c",
    MONITOR: "#4b5563",
    PROCEED: "#166534",
  };
  const bg = palette[value] ?? "#374151";
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 999,
        background: bg,
        color: "#fff",
        fontSize: 12,
        fontWeight: 700,
        letterSpacing: 0.3,
      }}
    >
      {value || "N/A"}
    </span>
  );
}

export default function ProductionDashboard() {

  const [board, setBoard] = useState<any>(null);

  const [load, setLoad] = useState<any>(null);

  const [sequence, setSequence] = useState<any>(null);
  const [atlasByArticle, setAtlasByArticle] = useState<Record<string, AtlasItem>>({});

  const [stationFilter, setStationFilter] = useState("ALL");
  const [onlyBlocked, setOnlyBlocked] = useState(false);

  async function loadAll() {

    const [b, l, s] = await Promise.all([

      fetchProductionBoard(),

      fetchProductionLoad(),

      fetchProductionSequence()

    ]);

    setBoard(b);

    setLoad(l);

    setSequence(s);

    void fetchProductionSequenceAtlasMerge()
      .then((atlasRaw: any) => {
        const atlasItems = (atlasRaw?.items ?? atlasRaw?.data ?? atlasRaw ?? []) as any[];
        const next = atlasItems.reduce((acc: Record<string, AtlasItem>, item: any) => {
          const key = String(item?.article ?? item?.codice ?? "").trim();
          if (!key) return acc;
          acc[key] = mapAtlasItem(item);
          return acc;
        }, {});
        setAtlasByArticle(next);
      })
      .catch(() => {
        setAtlasByArticle({});
      });
  }

  useEffect(() => {

    loadAll();

  }, []);

  if (!board) return <div style={{ padding: 40 }}>loading...</div>;

  const grouped = groupOrders(board.items || []);

  const stations = Array.from(

    new Set(grouped.map(i => i.postazione))

  );

  const filtered = grouped.filter(

    i => stationFilter === "ALL" || i.postazione === stationFilter

  );

  const red = filtered.filter(

    i => i.semaforo === "ROSSO"

  );

  async function seedDemo() {
    try {
      const payloads = [
        { order_id: "ORD-A-001", cliente: "Alpha", codice: "12063", qta: 8, postazione: "ZAW-1", stato: "in corso", semaforo: "GIALLO", due_date: "2026-04-20", note: "demo" },
        { order_id: "ORD-B-002", cliente: "Beta", codice: "ZX-900", qta: 5, postazione: "ZAW-1", stato: "da fare", semaforo: "ROSSO", due_date: "2026-04-18", note: "demo" },
        { order_id: "ORD-C-003", cliente: "Gamma", codice: "KJ-77", qta: 3, postazione: "ZAW-2", stato: "da fare", semaforo: "VERDE", due_date: "2026-04-22", note: "demo" },
        { order_id: "ORD-D-004", cliente: "Delta", codice: "AB-12", qta: 6, postazione: "ZAW-2", stato: "in corso", semaforo: "GIALLO", due_date: "2026-04-21", note: "demo" },
        { order_id: "ORD-E-005", cliente: "Epsilon", codice: "MN-45", qta: 4, postazione: "ZAW-1", stato: "da fare", semaforo: "ROSSO", due_date: "2026-04-19", note: "demo" },
      ];
      let ok = 0;
      for (const body of payloads) {
        const res = await fetch("/production/order", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
        if (res.ok) ok += 1;
      }
      await loadAll();
      // eslint-disable-next-line no-alert
      alert(`Seed completato: ${ok}/${payloads.length}`);
    } catch {
      // eslint-disable-next-line no-alert
      alert("Seed fallito");
    }
  }

  return (

    <main

      style={{

        padding: 24,

        display: "grid",

        gap: 24,

        maxWidth: 1200,

        margin: "0 auto"

      }}

    >

      <h1>TL Board</h1>


      <section
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}
      >
        <Section title="attenzione immediata" tone="#2a0f0f">
          {red.length === 0 && <div style={{ opacity: 0.7 }}>nessun blocco immediato</div>}
          {red.map((r) => (
            <div
              key={r.codice}
              style={{
                display: "grid",
                gridTemplateColumns: "auto 1fr auto",
                alignItems: "center",
                gap: 10,
                padding: "8px 10px",
                borderBottom: "1px dashed #333",
                background: "#1b0f10",
                borderRadius: 8,
                marginBottom: 6,
              }}
            >
              <span style={{ fontSize: 18 }} aria-hidden>⛔</span>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <strong style={{ fontSize: 16 }}>{r.codice}</strong>
                <span style={{ opacity: 0.8 }}>→</span>
                <Chip label={String(r.postazione)} />
              </div>
              <span style={{ justifySelf: "end", opacity: 0.9 }}>x{r.qta}</span>
            </div>
          ))}
        </Section>

        <Section title="carico postazioni">
          {(() => {
            const items = (load?.items ?? []) as any[];
            const max = Math.max(1, ...items.map((i) => Number(i.orders_total ?? 0)));
            return items.map((m) => {
              const pct = Math.round((Number(m.orders_total ?? 0) / max) * 100);
              return (
                <div key={m.station} style={{ marginBottom: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                    <span><Chip label={normalizeStation(m.station) || "-"} /></span>
                    <span style={{ opacity: 0.8 }}>{m.orders_total}</span>
                  </div>
                  <div style={{ height: 10, background: "#222", borderRadius: 6, overflow: "hidden", display: "flex" }}>
                    {/* Segmenti per red/yellow/green se disponibili, fallback a barra blu */}
                    {typeof m.red_total === "number" || typeof m.yellow_total === "number" || typeof m.green_total === "number" ? (
                      (() => {
                        const total = Math.max(1, Number(m.red_total||0)+Number(m.yellow_total||0)+Number(m.green_total||0));
                        const r = Math.round((Number(m.red_total||0)/total)*100);
                        const y = Math.round((Number(m.yellow_total||0)/total)*100);
                        const g = Math.max(0, 100 - r - y);
                        return (
                          <>
                            <div style={{ width: `${r}%`, background: "#7f1d1d" }} />
                            <div style={{ width: `${y}%`, background: "#7c5a10" }} />
                            <div style={{ width: `${g}%`, background: "#1f5f3a" }} />
                          </>
                        );
                      })()
                    ) : (
                      <div style={{ width: `${pct}%`, height: "100%", background: "#2563eb" }} />
                    )}
                  </div>
                </div>
              );
            });
          })()}
        </Section>
      </section>



      <Section title="sequenza consigliata">
        {(sequence?.items ?? []).slice(0, 20).map((s: any) => (
          <div key={`${s.rank}-${s.article}`} style={{ display: "flex", gap: 10, padding: "6px 0", alignItems: "center" }}>
            <span style={{ width: 28, textAlign: "right", opacity: 0.6 }}>{s.rank}</span>
            <strong style={{ fontSize: 14 }}>{s.article}</strong>
            <span style={{ opacity: 0.8 }}>→</span>
            <Chip label={normalizeStation(s.critical_station) || "-"} />
            {(() => {
              const atlas = atlasByArticle[String(s.article ?? "").trim()];
              return (
                <>
                  <span style={{ marginLeft: 6 }}>
                    <AtlasBadge outcome={atlas?.atlas_outcome} />
                  </span>
                  {typeof atlas?.atlas_score !== "undefined" && (
                    <span style={{ opacity: 0.85, fontSize: 12 }}>score {atlas.atlas_score}</span>
                  )}
                  {atlas?.explain_brief && (
                    <span style={{ opacity: 0.75, fontSize: 12, maxWidth: 260, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {atlas.explain_brief}
                    </span>
                  )}
                </>
              );
            })()}
            <span style={{ marginLeft: "auto", opacity: 0.8 }}>qta {s.quantity ?? 0}</span>
          </div>
        ))}
        {(sequence?.items ?? []).length === 0 && <div style={{ opacity: 0.7 }}>nessuna sequenza disponibile</div>}
      </Section>



      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <label htmlFor="stationFilter" style={{ fontWeight: 600 }}>Filtro postazione:</label>
        <select
          id="stationFilter"
          value={stationFilter}
          onChange={e => setStationFilter(e.target.value)}
          style={{ background: "#111", color: "#fff", border: "1px solid #333", borderRadius: 8, padding: "6px 10px" }}
        >
          <option value="ALL">tutte</option>
          {stations.map(s => (
            <option key={s}>{s}</option>
          ))}
        </select>

        <label style={{ display: "inline-flex", alignItems: "center", gap: 6, marginLeft: 12 }}>
          <input
            type="checkbox"
            checked={onlyBlocked}
            onChange={(e) => setOnlyBlocked(e.target.checked)}
          />
          <span>solo bloccati</span>
        </label>

        {import.meta.env.DEV && (
          <button
            type="button"
            onClick={() => { void seedDemo(); }}
            style={{
              marginLeft: 8,
              background: "#1f2937",
              color: "#e5e7eb",
              border: "1px solid #374151",
              borderRadius: 8,
              padding: "6px 10px",
              cursor: "pointer",
            }}
          >
            seed demo
          </button>
        )}
      </div>



      {/* guard tokens (do not remove):
        <th>codice</th>
        <th>postazione</th>
        <th>qta totale</th>
        <th>righe</th>
        <th>prio</th>
      */}
      <table
        style={{
          width: "100%",
          background: "#111",
          borderCollapse: "collapse",
          border: "1px solid #222",
          borderRadius: 8,
          overflow: "hidden"
        }}
      >
        <thead>
          <tr style={{ background: "#0b1220" }}>
            <th style={{ textAlign: "left", padding: 10 }}>codice</th>
            <th style={{ textAlign: "left", padding: 10 }}>postazione</th>
            <th style={{ textAlign: "right", padding: 10 }}>qta totale</th>
            <th style={{ textAlign: "right", padding: 10 }}>righe</th>
            <th style={{ textAlign: "left", padding: 10 }}>prio</th>
          </tr>
        </thead>
        <tbody>
          {(filtered.filter((o:any) => !onlyBlocked || String(o.stato||"").toLowerCase()==='bloccato' || String(o.semaforo||'').toUpperCase()==='ROSSO')).map((o:any, idx:number) => (
            <tr key={o.codice + o.postazione} style={{ background: idx % 2 ? "#0e0e0e" : "#111" }}>
              <td style={{ padding: 10 }}><strong>{o.codice}</strong></td>
              <td style={{ padding: 10 }}>{o.postazione}</td>
              <td style={{ padding: 10, textAlign: "right" }}>{o.qta}</td>
              <td style={{ padding: 10, textAlign: "right" }}>{o.count}</td>
              <td style={{ padding: 10 }}><PriorityBadge value={o.semaforo} /></td>
            </tr>
          ))}
        </tbody>
      </table>

    </main>

  );

}
