import { useEffect, useMemo, useState } from "react";
import {
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionTurnPlan,
} from "../services/production";

type BoardItem = {
  order_id?: string;
  codice?: string;
  postazione?: string;
  stato?: string;
  semaforo?: string;
  qta?: number;
};

type LoadItem = {
  station?: string;
  orders_total?: number;
  blocked_total?: number;
  red_total?: number;
  yellow_total?: number;
  green_total?: number;
  quantity_total?: number;
};

type SequenceItem = {
  rank?: number;
  article?: string;
  quantity?: number;
  due_date?: string | null;
  customer_priority?: string;
  critical_station?: string;
  tl_action?: string;
};

type TurnPlanItem = {
  slot?: number;
  shift?: string;
  team_leader?: string;
  station?: string;
  article?: string;
  quantity?: number;
  customer_priority?: string;
};

function normalizeStationName(raw?: string) {
  const value = String(raw ?? "").trim().toUpperCase();

  if (!value) return "";

  return value
    .replaceAll("_", "-")
    .replace("LINEA1", "LINEA-1")
    .replace("LINEA-A", "LINEA-A")
    .replace("LINEA-1", "LINEA-1")
    .replace("ZAW1", "ZAW-1")
    .replace("ZAW2", "ZAW-2");
}

function dedupeSequence(items: SequenceItem[]) {
  const map = new Map<string, SequenceItem>();

  for (const item of items) {
    const key = `${item.article ?? ""}::${normalizeStationName(item.critical_station)}`;

    if (!map.has(key)) {
      map.set(key, {
        ...item,
        critical_station: normalizeStationName(item.critical_station),
      });
      continue;
    }

    const prev = map.get(key)!;
    prev.quantity = Number(prev.quantity ?? 0) + Number(item.quantity ?? 0);
    prev.rank = Math.min(Number(prev.rank ?? 999999), Number(item.rank ?? 999999));
  }

  return Array.from(map.values()).sort(
    (a, b) => Number(a.rank ?? 999999) - Number(b.rank ?? 999999),
  );
}

function aggregateBoard(items: BoardItem[]) {
  const map = new Map<string, BoardItem & { rows: number }>();

  for (const item of items) {
    const codice = String(item.codice ?? "").trim();
    const postazione = normalizeStationName(item.postazione);
    const key = `${codice}::${postazione}`;

    if (!map.has(key)) {
      map.set(key, {
        ...item,
        postazione,
        qta: Number(item.qta ?? 0),
        rows: 1,
      });
      continue;
    }

    const prev = map.get(key)!;
    prev.qta = Number(prev.qta ?? 0) + Number(item.qta ?? 0);
    prev.rows += 1;

    if (String(item.semaforo ?? "").toUpperCase() === "ROSSO") {
      prev.semaforo = "ROSSO";
    } else if (
      String(prev.semaforo ?? "").toUpperCase() !== "ROSSO" &&
      String(item.semaforo ?? "").toUpperCase() === "GIALLO"
    ) {
      prev.semaforo = "GIALLO";
    }

    if (String(item.stato ?? "").toLowerCase() === "bloccato") {
      prev.stato = "bloccato";
    }
  }

  return Array.from(map.values()).sort((a, b) => {
    const sa = String(a.semaforo ?? "").toUpperCase();
    const sb = String(b.semaforo ?? "").toUpperCase();

    const weight = (v: string) => {
      if (v === "ROSSO") return 0;
      if (v === "GIALLO") return 1;
      if (v === "VERDE") return 2;
      return 3;
    };

    return weight(sa) - weight(sb);
  });
}

function statusSignal(stato?: string, semaforo?: string) {
  const s = String(stato ?? "").trim().toLowerCase();
  const light = String(semaforo ?? "").trim().toUpperCase();

  if (s === "bloccato" || light === "ROSSO") {
    return { icon: "⛔", label: "BLOCCO", tone: "#ef4444" };
  }

  if (light === "GIALLO") {
    return { icon: "⚠️", label: "ATTENZIONE", tone: "#eab308" };
  }

  if (light === "VERDE") {
    return { icon: "🟢", label: "OK", tone: "#22c55e" };
  }

  return { icon: "⚪", label: "NEUTRO", tone: "#a1a1aa" };
}

function prioritySignal(priority?: string) {
  const value = String(priority ?? "").toUpperCase();

  if (value === "CRITICA" || value === "ALTA") {
    return { icon: "🔺", tone: "#ef4444" };
  }

  return { icon: "🔵", tone: "#38bdf8" };
}

function cardStyle() {
  return {
    border: "1px solid #333",
    padding: 16,
    borderRadius: 12,
    background: "#111",
  } as const;
}

export default function Dashboard() {
  const [board, setBoard] = useState<BoardItem[]>([]);
  const [load, setLoad] = useState<LoadItem[]>([]);
  const [sequence, setSequence] = useState<SequenceItem[]>([]);
  const [turnPlan, setTurnPlan] = useState<TurnPlanItem[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [b, l, s, t] = await Promise.all([
          fetchProductionBoard(),
          fetchProductionLoad(),
          fetchProductionSequence(),
          fetchProductionTurnPlan(),
        ]);

        const rawBoard: BoardItem[] = b?.items ?? [];
        const rawLoad: LoadItem[] = l?.items ?? [];
        const rawSequence: SequenceItem[] = s?.items ?? [];
        const rawTurnPlan: TurnPlanItem[] = t?.items ?? [];

        setBoard(
          aggregateBoard(
            rawBoard.map((item) => ({
              ...item,
              postazione: normalizeStationName(item.postazione),
            })),
          ),
        );

        setLoad(
          rawLoad.map((item) => ({
            ...item,
            station: normalizeStationName(item.station),
          })),
        );

        setSequence(dedupeSequence(rawSequence));

        setTurnPlan(
          rawTurnPlan.map((item) => ({
            ...item,
            station: normalizeStationName(item.station),
          })),
        );
      } catch {
        setBoard([]);
        setLoad([]);
        setSequence([]);
        setTurnPlan([]);
      }
    }

    void loadData();
    const intervalId = setInterval(() => {
      void loadData();
    }, 5000);

    return () => clearInterval(intervalId);
  }, []);

  const totals = useMemo(() => {
    return {
      orders: load.reduce((a, b) => a + Number(b.orders_total ?? 0), 0),
      blocked: load.reduce((a, b) => a + Number(b.blocked_total ?? 0), 0),
      qty: load.reduce((a, b) => a + Number(b.quantity_total ?? 0), 0),
    };
  }, [load]);

  const bottleneck = useMemo(() => {
    if (load.length === 0) return null;

    return [...load].sort((a, b) => {
      const scoreA =
        Number(a.blocked_total ?? 0) * 100 +
        Number(a.red_total ?? 0) * 10 +
        Number(a.orders_total ?? 0);
      const scoreB =
        Number(b.blocked_total ?? 0) * 100 +
        Number(b.red_total ?? 0) * 10 +
        Number(b.orders_total ?? 0);

      return scoreB - scoreA;
    })[0];
  }, [load]);

  return (
    <div
      style={{
        background: "#0a0a0a",
        color: "#e5e5e5",
        minHeight: "100vh",
        padding: 20,
        display: "grid",
        gap: 20,
      }}
    >
      <h1 style={{ margin: 0 }}>PROMETEO TL</h1>

      <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
        <div style={cardStyle()}>📦 ordini {totals.orders}</div>
        <div style={cardStyle()}>⛔ blocchi {totals.blocked}</div>
        <div style={cardStyle()}>🚚 qta {totals.qty}</div>
        <div style={cardStyle()}>
          🔥 collo di bottiglia{" "}
          <strong>{bottleneck?.station ?? "-"}</strong>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 20 }}>
        <div style={cardStyle()}>
          <h2 style={{ marginTop: 0 }}>Sequence radar</h2>

          {sequence.length === 0 ? (
            <div>Nessuna sequenza disponibile.</div>
          ) : (
            sequence.map((s, idx) => {
              const p = prioritySignal(s.customer_priority);

              return (
                <div
                  key={`${s.article}-${s.critical_station}-${idx}`}
                  style={{
                    border: "1px solid #2a2a2a",
                    marginBottom: 10,
                    padding: 12,
                    borderRadius: 8,
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                    alignItems: "center",
                  }}
                >
                  <div>
                    <strong>{s.article}</strong> → {s.critical_station}
                    <div style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
                      qta {s.quantity ?? 0} · {s.tl_action ?? "azione non definita"}
                    </div>
                  </div>

                  <div style={{ color: p.tone, fontWeight: 700 }}>{p.icon}</div>
                </div>
              );
            })
          )}
        </div>

        <div style={cardStyle()}>
          <h2 style={{ marginTop: 0 }}>ZAW status</h2>

          {load.map((x) => {
            const blocked = Number(x.blocked_total ?? 0) > 0;
            const red = Number(x.red_total ?? 0) > 0;

            return (
              <div
                key={x.station}
                style={{
                  border: `1px solid ${blocked || red ? "#7f1d1d" : "#333"}`,
                  padding: 14,
                  borderRadius: 10,
                  marginBottom: 10,
                  background: blocked || red ? "#2a1111" : "#111",
                }}
              >
                <div style={{ fontWeight: 700 }}>{x.station}</div>
                <div style={{ opacity: 0.85, marginTop: 6 }}>
                  ordini {x.orders_total} · blocchi {x.blocked_total} · qta {x.quantity_total}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={cardStyle()}>
        <h2 style={{ marginTop: 0 }}>Board segnali</h2>

        {board.length === 0 ? (
          <div>Nessun segnale disponibile.</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">segnale</th>
                <th align="left">codice</th>
                <th align="left">postazione</th>
                <th align="left">qta</th>
                <th align="left">righe</th>
              </tr>
            </thead>
            <tbody>
              {board.map((b) => {
                const signal = statusSignal(b.stato, b.semaforo);

                return (
                  <tr
                    key={`${b.codice}-${b.postazione}`}
                    style={{ borderTop: "1px solid #222" }}
                  >
                    <td style={{ color: signal.tone }}>
                      {signal.icon} {signal.label}
                    </td>
                    <td>{b.codice}</td>
                    <td>{b.postazione}</td>
                    <td>{b.qta ?? 0}</td>
                    <td>{(b as BoardItem & { rows?: number }).rows ?? 1}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <div style={cardStyle()}>
        <h2 style={{ marginTop: 0 }}>Turn plan</h2>

        {turnPlan.length === 0 ? (
          <div>Nessun turn plan disponibile.</div>
        ) : (
          turnPlan.map((t, idx) => (
            <div
              key={`${t.slot}-${t.team_leader}-${idx}`}
              style={{
                border: "1px solid #2a2a2a",
                marginBottom: 10,
                padding: 12,
                borderRadius: 8,
              }}
            >
              🎯 <strong>{t.team_leader}</strong> → {t.station}
              <div style={{ opacity: 0.75, fontSize: 12, marginTop: 4 }}>
                {t.shift} · {t.article} · qta {t.quantity ?? 0}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
