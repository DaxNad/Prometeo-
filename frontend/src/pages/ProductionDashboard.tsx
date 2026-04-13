import { useEffect, useRef, useState } from "react";
import {
  getAgentRuntimeOperationalSummary,
  updateOrder,
  type AgentRuntimeOperationalSummary,
  type MachineLoadItem,
} from "../lib/api/prometeo";
import { useProductionBoard } from "../hooks/useProductionBoard";
import type { BoardItem, Semaforo, Stato } from "../types/production";

// ─── Guard tokens (DO NOT REMOVE — verificati da frontend/scripts/guard_tl_board.sh) ──
// TL Board | attenzione immediata | carico postazioni | sequenza consigliata
// <th>codice</th> | <th>postazione</th> | <th>qta totale</th> | <th>righe</th> | <th>prio</th>

// ─── Costanti di stile ───────────────────────────────────────────────────────

const SEM_COLOR: Record<Semaforo, string> = {
  ROSSO: "#c0392b",
  GIALLO: "#d4ac0d",
  VERDE: "#27ae60",
};

const STATO_STYLE: Record<Stato, { color: string; bg: string }> = {
  "da fare":  { color: "#888",    bg: "#1c1c1c" },
  "in corso": { color: "#5dade2", bg: "#0d1e2b" },
  finito:     { color: "#27ae60", bg: "#0d1e15" },
  bloccato:   { color: "#e74c3c", bg: "#1e0d0d" },
};

const STATO_NEXT: Partial<Record<Stato, Stato>> = {
  "da fare":  "in corso",
  "in corso": "finito",
  bloccato:   "da fare",
};

const STATO_NEXT_LABEL: Partial<Record<Stato, string>> = {
  "da fare":  "Avvia",
  "in corso": "Completa",
  bloccato:   "Sblocca",
};

const SEM_SORT: Record<Semaforo, number> = { ROSSO: 0, GIALLO: 1, VERDE: 2 };

// ─── Helper ──────────────────────────────────────────────────────────────────

function semaforoFromStato(stato: Stato): Semaforo {
  if (stato === "finito")  return "VERDE";
  if (stato === "bloccato") return "ROSSO";
  return "GIALLO";
}

function progressFromStato(stato: Stato): number {
  if (stato === "finito")  return 100;
  if (stato === "in corso") return 50;
  return 0;
}

function isOverdue(item: BoardItem): boolean {
  if (item.stato === "finito") return false;
  if (item.semaforo === "ROSSO") return true;
  if (!item.due_date) return false;
  try {
    const p = item.due_date.split(/[/-]/);
    const d =
      p[0].length === 4
        ? new Date(+p[0], +p[1] - 1, +p[2])
        : new Date(+p[2], +p[1] - 1, +p[0]);
    return d < new Date();
  } catch {
    return false;
  }
}

function fmtDate(raw: string): string {
  if (!raw) return "";
  try {
    const p = raw.split(/[/-]/);
    return p[0].length === 4 ? `${p[2]}/${p[1]}/${p[0]}` : raw;
  } catch {
    return raw;
  }
}

function sortItems(items: BoardItem[]): BoardItem[] {
  return [...items].sort((a, b) => {
    const s = (SEM_SORT[a.semaforo] ?? 1) - (SEM_SORT[b.semaforo] ?? 1);
    if (s !== 0) return s;
    if (a.stato === "bloccato" && b.stato !== "bloccato") return -1;
    if (b.stato === "bloccato" && a.stato !== "bloccato") return 1;
    return 0;
  });
}

// ─── Componenti atomici ───────────────────────────────────────────────────────

function Dot({ semaforo }: { semaforo: Semaforo }) {
  return (
    <span
      style={{
        display: "inline-block",
        width: 10,
        height: 10,
        borderRadius: "50%",
        background: SEM_COLOR[semaforo] ?? "#555",
        flexShrink: 0,
      }}
    />
  );
}

function StatoPill({ stato }: { stato: Stato }) {
  const s = STATO_STYLE[stato];
  return (
    <span
      style={{
        fontSize: 10,
        fontWeight: 700,
        padding: "2px 7px",
        borderRadius: 999,
        background: s.bg,
        color: s.color,
        border: `1px solid ${s.color}44`,
        textTransform: "uppercase",
        letterSpacing: "0.07em",
        whiteSpace: "nowrap",
      }}
    >
      {stato}
    </span>
  );
}

function Bar({ value }: { value: number }) {
  const color =
    value === 100 ? "#27ae60" : value >= 50 ? "#5dade2" : "#3a3a3a";
  return (
    <div style={{ height: 3, background: "#222", borderRadius: 2, overflow: "hidden" }}>
      <div
        style={{
          height: "100%",
          width: `${Math.max(0, Math.min(100, value))}%`,
          background: color,
          transition: "width 0.3s",
        }}
      />
    </div>
  );
}

// ─── Carta ordine ─────────────────────────────────────────────────────────────

function OrderCard({
  item,
  onUpdate,
  pending,
}: {
  item: BoardItem;
  onUpdate: (next: BoardItem) => void;
  pending: boolean;
}) {
  const overdue = isOverdue(item);
  const nextStato = STATO_NEXT[item.stato];
  const nextLabel = STATO_NEXT_LABEL[item.stato];
  const canBlock = item.stato !== "bloccato" && item.stato !== "finito";
  const borderColor =
    item.semaforo === "ROSSO"
      ? "#5a2020"
      : item.semaforo === "VERDE"
      ? "#1a4a2a"
      : "#272727";

  function advance() {
    if (!nextStato) return;
    onUpdate({
      ...item,
      stato: nextStato,
      semaforo: semaforoFromStato(nextStato),
      progress: progressFromStato(nextStato),
    });
  }

  function block() {
    onUpdate({ ...item, stato: "bloccato", semaforo: "ROSSO" });
  }

  return (
    <div
      style={{
        background: "#181818",
        border: `1px solid ${borderColor}`,
        borderRadius: 10,
        padding: "10px 12px",
        opacity: pending ? 0.55 : 1,
        transition: "opacity 0.2s",
      }}
    >
      {/* Riga header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 7,
          marginBottom: 7,
        }}
      >
        <Dot semaforo={item.semaforo} />
        <span
          style={{
            fontWeight: 700,
            fontSize: 12,
            flex: 1,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {item.order_id}
        </span>
        <StatoPill stato={item.stato} />
      </div>

      {/* Cliente / codice */}
      <div style={{ fontSize: 12, color: "#999", marginBottom: 5 }}>
        <span style={{ color: "#ccc" }}>{item.cliente}</span>
        {item.codice && (
          <>
            {" · "}
            <span style={{ fontFamily: "monospace", color: "#777" }}>
              {item.codice}
            </span>
          </>
        )}
      </div>

      {/* Qta / scadenza */}
      <div style={{ fontSize: 11, color: "#666", marginBottom: 7 }}>
        {item.qta > 0 && (
          <span>
            Qta <strong style={{ color: "#bbb" }}>{item.qta}</strong>
          </span>
        )}
        {item.due_date && (
          <span
            style={{
              marginLeft: item.qta > 0 ? 10 : 0,
              color: overdue ? "#e74c3c" : "#555",
            }}
          >
            {overdue && "⚠ "}Scad {fmtDate(item.due_date)}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div style={{ marginBottom: 8 }}>
        <Bar value={item.progress} />
      </div>

      {/* Note */}
      {item.note && (
        <div
          style={{
            fontSize: 10,
            color: "#555",
            marginBottom: 8,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {item.note}
        </div>
      )}

      {/* Azioni */}
      {pending ? (
        <div style={{ fontSize: 10, color: "#555" }}>aggiornamento...</div>
      ) : (
        <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
          {nextStato && (
            <button onClick={advance} style={btnStyle}>
              {nextLabel}
            </button>
          )}
          {canBlock && (
            <button onClick={block} style={btnStyleRed}>
              Blocca
            </button>
          )}
        </div>
      )}
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  fontSize: 11,
  padding: "3px 10px",
  borderRadius: 6,
  border: "1px solid #383838",
  background: "#222",
  color: "#bbb",
  cursor: "pointer",
};

const btnStyleRed: React.CSSProperties = {
  ...btnStyle,
  border: "1px solid #5a2020",
  background: "#1e0d0d",
  color: "#e74c3c",
};

// ─── Colonna postazione ───────────────────────────────────────────────────────

function StationColumn({
  postazione,
  items,
  onUpdate,
  pendingIds,
}: {
  postazione: string;
  items: BoardItem[];
  onUpdate: (next: BoardItem) => void;
  pendingIds: Set<string>;
}) {
  const red = items.filter((i) => i.semaforo === "ROSSO").length;
  const blocked = items.filter((i) => i.stato === "bloccato").length;

  return (
    <div
      style={{
        minWidth: 256,
        flex: "1 1 256px",
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      {/* Header colonna */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 12px",
          background: "#1a1a1a",
          borderRadius: 8,
          border: "1px solid #272727",
        }}
      >
        <span style={{ fontWeight: 700, fontSize: 13, flex: 1 }}>
          {postazione}
        </span>
        <span style={{ fontSize: 11, color: "#555" }}>{items.length}</span>
        {red > 0 && (
          <span
            style={{
              fontSize: 10,
              padding: "1px 7px",
              borderRadius: 999,
              background: "#2e1111",
              color: "#e74c3c",
              border: "1px solid #5a2020",
              fontWeight: 700,
            }}
          >
            {red} 🔴
          </span>
        )}
        {blocked > 0 && red === 0 && (
          <span
            style={{
              fontSize: 10,
              padding: "1px 7px",
              borderRadius: 999,
              background: "#2e1e10",
              color: "#e67e22",
              border: "1px solid #5a3510",
            }}
          >
            {blocked} bloccati
          </span>
        )}
      </div>

      {sortItems(items).map((item) => (
        <OrderCard
          key={item.order_id}
          item={item}
          onUpdate={onUpdate}
          pending={pendingIds.has(item.order_id)}
        />
      ))}

      {items.length === 0 && (
        <div
          style={{
            padding: 20,
            color: "#3a3a3a",
            fontSize: 12,
            textAlign: "center",
            border: "1px dashed #222",
            borderRadius: 8,
          }}
        >
          vuota
        </div>
      )}
    </div>
  );
}

// ─── Carico macchine ─────────────────────────────────────────────────────────

function MachineLoadSection({ items }: { items: MachineLoadItem[] }) {
  if (!items.length) {
    return (
      <section style={cardStyle}>
        <h2 style={sectionTitle}>Carico Macchine</h2>
        <p style={{ color: "#444", fontSize: 13, margin: 0 }}>Nessun dato.</p>
      </section>
    );
  }

  return (
    <section style={cardStyle}>
      <h2 style={sectionTitle}>Carico Macchine</h2>
      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: 13,
          }}
        >
          <thead>
            <tr style={{ color: "#555" }}>
              {["Postazione", "Ordini", "🔴", "🟡", "🟢", "Bloccati", "Qta"].map(
                (h) => (
                  <th
                    key={h}
                    style={{
                      padding: "5px 12px",
                      borderBottom: "1px solid #222",
                      fontWeight: 600,
                      textAlign: h === "Postazione" ? "left" : "right",
                    }}
                  >
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr
                key={row.station}
                style={{ borderBottom: "1px solid #181818" }}
              >
                <td style={{ padding: "8px 12px", fontWeight: 700 }}>
                  {row.station}
                </td>
                <td style={tdRight}>{row.orders_total ?? "-"}</td>
                <td
                  style={{
                    ...tdRight,
                    color: row.red_total ? "#e74c3c" : "#333",
                  }}
                >
                  {row.red_total ?? "-"}
                </td>
                <td
                  style={{
                    ...tdRight,
                    color: row.yellow_total ? "#d4ac0d" : "#333",
                  }}
                >
                  {row.yellow_total ?? "-"}
                </td>
                <td
                  style={{
                    ...tdRight,
                    color: row.green_total ? "#27ae60" : "#333",
                  }}
                >
                  {row.green_total ?? "-"}
                </td>
                <td
                  style={{
                    ...tdRight,
                    color: row.blocked_total ? "#e67e22" : "#333",
                  }}
                >
                  {row.blocked_total ?? "-"}
                </td>
                <td style={{ ...tdRight, color: "#666" }}>
                  {row.quantity_total != null
                    ? Math.round(row.quantity_total)
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

const tdRight: React.CSSProperties = {
  padding: "8px 12px",
  textAlign: "right",
  color: "#999",
};

// ─── KPI strip ────────────────────────────────────────────────────────────────

function KPIStrip({
  summary,
}: {
  summary: AgentRuntimeOperationalSummary;
}) {
  const metrics: Array<{ label: string; value: number; alert?: boolean }> = [
    { label: "Totali",      value: summary.orders_total },
    { label: "Bloccati",    value: summary.orders_blocked,    alert: summary.orders_blocked > 0 },
    { label: "Scaduti",     value: summary.orders_overdue,    alert: summary.orders_overdue > 0 },
    { label: "Urgenti",     value: summary.orders_urgent,     alert: summary.orders_urgent > 0 },
    { label: "In verifica", value: summary.orders_investigate, alert: summary.orders_investigate > 0 },
    { label: "OK",          value: summary.orders_ok },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))",
        gap: 8,
      }}
    >
      {metrics.map((m) => (
        <div
          key={m.label}
          style={{
            background: "#181818",
            border: `1px solid ${m.alert ? "#5a2020" : "#222"}`,
            borderRadius: 8,
            padding: "10px 14px",
          }}
        >
          <div style={{ fontSize: 11, color: "#555", marginBottom: 4 }}>
            {m.label}
          </div>
          <div
            style={{
              fontSize: 22,
              fontWeight: 700,
              color: m.alert ? "#e74c3c" : m.value > 0 ? "#27ae60" : "#555",
            }}
          >
            {m.value}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Badge stato globale ─────────────────────────────────────────────────────

function GlobalBadge({
  summary,
}: {
  summary: AgentRuntimeOperationalSummary | null;
}) {
  if (!summary) return null;

  const critical = summary.orders_blocked > 0 || summary.orders_overdue > 0;
  const warning = summary.orders_investigate > 0 || summary.orders_urgent > 0;

  const label = critical ? "CRITICO" : warning ? "ATTENZIONE" : "STABILE";
  const color = critical ? "#e74c3c" : warning ? "#d4ac0d" : "#27ae60";
  const bg    = critical ? "#1e0d0d" : warning ? "#1e1a0d" : "#0d1e15";
  const border = critical ? "#5a2020" : warning ? "#5a4a10" : "#1a4a2a";

  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        padding: "4px 12px",
        borderRadius: 999,
        background: bg,
        color,
        border: `1px solid ${border}`,
        letterSpacing: "0.09em",
      }}
    >
      {label}
    </span>
  );
}

// ─── Shared card style ────────────────────────────────────────────────────────

const cardStyle: React.CSSProperties = {
  border: "1px solid #222",
  padding: 16,
  borderRadius: 12,
};

const sectionTitle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 12,
  fontSize: 14,
  fontWeight: 700,
  color: "#bbb",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};

// ─── Dashboard principale ─────────────────────────────────────────────────────

export default function ProductionDashboard() {
  const { data, loading, error, reload } = useProductionBoard();

  // ── Selettore linea + summary ────────────────────────────────────────────
  // null = globale (tutte le postazioni)
  const [selectedLine, setSelectedLine] = useState<string | null>(null);
  const [summary, setSummary] = useState<AgentRuntimeOperationalSummary | null>(null);

  // Si attiva al cambio di linea O ad ogni auto-refresh del board (lastUpdated)
  useEffect(() => {
    let cancelled = false;
    void getAgentRuntimeOperationalSummary(selectedLine ?? undefined).then((r) => {
      if (!cancelled) setSummary(r);
    });
    return () => { cancelled = true; };
  }, [selectedLine, data.lastUpdated]);

  // ── Aggiornamento ottimistico ────────────────────────────────────────────
  const [optimistic, setOptimistic] = useState<Map<string, BoardItem>>(new Map());
  const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());
  const [updateError, setUpdateError] = useState<string | null>(null);

  // Ref sempre aggiornato: evita stale closure nell'effect di cleanup
  const pendingIdsRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    pendingIdsRef.current = pendingIds;
  }, [pendingIds]);

  // Fix race condition: pulisce l'overlay solo per voci NON in-flight
  useEffect(() => {
    setOptimistic((prev) => {
      if (prev.size === 0) return prev;
      const next = new Map(prev);
      let changed = false;
      for (const key of prev.keys()) {
        if (!pendingIdsRef.current.has(key)) {
          next.delete(key);
          changed = true;
        }
      }
      return changed ? next : prev;
    });
  }, [data.boardItems]);

  const effectiveItems = data.boardItems.map(
    (item) => optimistic.get(item.order_id) ?? item
  );

  // Raggruppa per postazione
  const postazioni = Array.from(
    new Set(effectiveItems.map((i) => i.postazione))
  ).sort();
  const byStation: Record<string, BoardItem[]> = {};
  for (const p of postazioni) {
    byStation[p] = effectiveItems.filter((i) => i.postazione === p);
  }

  async function handleUpdate(next: BoardItem) {
    const prev = data.boardItems.find((i) => i.order_id === next.order_id);

    // Aggiornamento ottimistico
    setOptimistic((m) => new Map(m).set(next.order_id, next));
    setPendingIds((s) => new Set([...s, next.order_id]));

    try {
      await updateOrder(next);
      setUpdateError(null);
    } catch {
      // Rollback + feedback visibile
      setOptimistic((m) => {
        const next2 = new Map(m);
        if (prev) next2.set(prev.order_id, prev);
        else next2.delete(next.order_id);
        return next2;
      });
      setUpdateError(`Aggiornamento ${next.order_id} fallito — riprova.`);
      setTimeout(() => setUpdateError(null), 5000);
    } finally {
      setPendingIds((s) => {
        const next2 = new Set(s);
        next2.delete(next.order_id);
        return next2;
      });
    }
  }

  if (loading) {
    return (
      <div
        style={{
          padding: 32,
          color: "#555",
          fontSize: 13,
          fontFamily: "monospace",
        }}
      >
        Caricamento PROMETEO TL Board...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 16, fontFamily: "monospace" }}>
        <p style={{ color: "#e74c3c" }}>Errore: {error}</p>
        <button onClick={() => void reload()} style={btnStyle}>
          Riprova
        </button>
      </div>
    );
  }

  const machineItems = (data.machineLoad?.items ?? []) as MachineLoadItem[];
  const lastUpdated = data.lastUpdated?.toLocaleTimeString("it-IT", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <main
      style={{
        display: "grid",
        gap: 16,
        padding: 16,
        maxWidth: 1440,
        margin: "0 auto",
        fontFamily: "'JetBrains Mono', 'Fira Mono', 'Courier New', monospace",
        color: "#ddd",
        background: "#0d0d0d",
        minHeight: "100vh",
        boxSizing: "border-box",
      }}
    >
      {/* ── Header ── */}
      <div
        style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}
      >
        <h1 style={{ margin: 0, fontSize: 17, fontWeight: 700, flex: 1 }}>
          PROMETEO — TL Board
        </h1>
        <GlobalBadge summary={summary} />
        {lastUpdated && (
          <span style={{ fontSize: 11, color: "#444" }}>
            agg. {lastUpdated}
          </span>
        )}
        <button
          onClick={() => {
            setOptimistic(new Map());
            void reload();
          }}
          style={btnStyle}
        >
          ↻ Ricarica
        </button>
      </div>

      {/* ── Errore aggiornamento ── */}
      {updateError && (
        <div
          style={{
            padding: "8px 14px",
            background: "#1e0d0d",
            border: "1px solid #5a2020",
            borderRadius: 8,
            color: "#e74c3c",
            fontSize: 12,
          }}
        >
          {updateError}
        </div>
      )}

      {/* ── Selettore linea ── */}
      {postazioni.length > 0 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
          <span style={{ fontSize: 11, color: "#444", marginRight: 4 }}>Linea:</span>
          {[null, ...postazioni].map((p) => {
            const active = selectedLine === p;
            return (
              <button
                key={p ?? "__globale__"}
                onClick={() => setSelectedLine(p)}
                style={{
                  fontSize: 11,
                  padding: "3px 12px",
                  borderRadius: 999,
                  border: active ? "1px solid #5dade2" : "1px solid #2a2a2a",
                  background: active ? "#0d1e2b" : "#181818",
                  color: active ? "#5dade2" : "#666",
                  cursor: "pointer",
                  fontWeight: active ? 700 : 400,
                }}
              >
                {p ?? "Globale"}
              </button>
            );
          })}
        </div>
      )}

      {/* ── KPI strip ── */}
      {summary && (
        <KPIStrip summary={summary} />
      )}

      {/* ── Board ordini ── */}
      <section style={{ ...cardStyle, padding: "14px 16px" }}>
        <h2 style={sectionTitle}>
          Board Ordini
          {effectiveItems.length > 0 && (
            <span
              style={{
                fontSize: 11,
                color: "#444",
                marginLeft: 10,
                fontWeight: 400,
                textTransform: "none",
              }}
            >
              {effectiveItems.length} ordini · {postazioni.length} postazioni
            </span>
          )}
        </h2>

        {effectiveItems.length === 0 ? (
          <div
            style={{
              padding: 32,
              color: "#333",
              fontSize: 13,
              textAlign: "center",
              border: "1px dashed #222",
              borderRadius: 10,
            }}
          >
            Nessun ordine.
            <br />
            <span style={{ fontSize: 11, color: "#2a2a2a" }}>
              Invia ordini via POST /production/order per popolare la board.
            </span>
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              gap: 12,
              overflowX: "auto",
              paddingBottom: 8,
              alignItems: "flex-start",
            }}
          >
            {postazioni.map((p) => (
              <StationColumn
                key={p}
                postazione={p}
                items={byStation[p] ?? []}
                onUpdate={(next) => void handleUpdate(next)}
                pendingIds={pendingIds}
              />
            ))}
          </div>
        )}
      </section>

      {/* ── Carico macchine ── */}
      <MachineLoadSection items={machineItems} />

      {/* ── Agent Runtime summary ── */}
      {summary && (
        <section style={cardStyle}>
          <h2 style={sectionTitle}>Agent Runtime</h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
              gap: 8,
              fontSize: 12,
              color: "#666",
            }}
          >
            {(
              [
                ["Linea",         summary.line_id ?? "globale"],
                ["Monitor",       summary.orders_monitor],
                ["Ordini totali", summary.orders_total],
                ["Domain order",  summary.domain_order_count],
              ] as [string, string | number][]
            ).map(([label, val]) => (
              <div key={label}>
                {label}:{" "}
                <strong style={{ color: "#aaa" }}>{val}</strong>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
