import { useEffect, useState } from "react"
import "./App.css"

const API = "/api"

type Order = {
  order_id: string
  cliente: string
  codice: string
  qta: number
  postazione: string
  stato: string
  progress: number
  semaforo: string
  due_date: string
  note: string
}

type LoadRow = {
  postazione: string
  orders_total: number
  orders_open: number
  orders_done: number
  red: number
  yellow: number
  green: number
}

export default function App() {
  const [board, setBoard] = useState<Order[]>([])
  const [delays, setDelays] = useState<Order[]>([])
  const [load, setLoad] = useState<LoadRow[]>([])
  const [loading, setLoading] = useState(true)
  const [busyOrderId, setBusyOrderId] = useState("")

  async function loadData() {
    setLoading(true)

    const [b, d, l] = await Promise.all([
      fetch(`${API}/production/board`).then((r) => r.json()),
      fetch(`${API}/production/delays`).then((r) => r.json()),
      fetch(`${API}/production/load`).then((r) => r.json()),
    ])

    setBoard(b.items || [])
    setDelays(d.items || [])
    setLoad(l.items || [])
    setLoading(false)
  }

  useEffect(() => {
    loadData()
    const t = setInterval(loadData, 5000)
    return () => clearInterval(t)
  }, [])

  async function patchOrder(orderId: string, payload: Record<string, unknown>) {
    setBusyOrderId(orderId)

    try {
      const res = await fetch(`${API}/production/order/${encodeURIComponent(orderId)}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || "PATCH ordine fallita")
      }

      await loadData()
    } finally {
      setBusyOrderId("")
    }
  }

  async function handleStart(order: Order) {
    const now = new Date().toLocaleString("sv-SE")

    await patchOrder(order.order_id, {
      "Stato (da fare/in corso/finito)": "in corso",
      "Data inizio": now,
      "Progress %": order.progress && Number(order.progress) > 0 ? order.progress : 10,
      "Semaforo scadenza": order.semaforo || "GIALLO",
    })
  }

  async function handleDone(order: Order) {
    const now = new Date().toLocaleString("sv-SE")

    await patchOrder(order.order_id, {
      "Stato (da fare/in corso/finito)": "finito",
      "Data fine": now,
      "Progress %": 100,
      "Semaforo scadenza": "VERDE",
    })
  }

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">PROMETEO</p>
          <h1>Dashboard Produzione</h1>
        </div>

        <button onClick={loadData} disabled={loading || !!busyOrderId}>
          aggiorna
        </button>
      </header>

      <section className="card">
        <h2>Board ordini</h2>

        {loading && <p>caricamento...</p>}

        {!loading && board.length === 0 && <p>nessun ordine disponibile</p>}

        {board.map((o) => (
          <div className="list-item" key={o.order_id}>
            <div>
              <strong>{o.order_id}</strong>
              <p>
                {o.cliente} · {o.codice}
              </p>
              <p>
                qta {o.qta} · progress {o.progress}%
              </p>
              <p>
                stato {o.stato}
              </p>
            </div>

            <div className="row-actions">
              <span className="badge neutral">{o.postazione}</span>

              <span
                className={`badge ${
                  o.semaforo === "ROSSO"
                    ? "danger"
                    : o.semaforo === "GIALLO"
                    ? "neutral"
                    : "success"
                }`}
              >
                {o.semaforo}
              </span>

              <button
                className="secondary-btn"
                onClick={() => handleStart(o)}
                disabled={!!busyOrderId || o.stato === "in corso" || o.stato === "finito"}
              >
                {busyOrderId === o.order_id ? "..." : "START"}
              </button>

              <button
                onClick={() => handleDone(o)}
                disabled={!!busyOrderId || o.stato === "finito"}
              >
                {busyOrderId === o.order_id ? "..." : "DONE"}
              </button>
            </div>
          </div>
        ))}
      </section>

      <section className="card">
        <h2>Ritardi</h2>

        {delays.length === 0 && <p>nessun ritardo</p>}

        {delays.map((o) => (
          <div className="list-item" key={o.order_id}>
            <strong>{o.order_id}</strong>
            <span className="badge danger">{o.semaforo}</span>
          </div>
        ))}
      </section>

      <section className="card">
        <h2>Carico postazioni</h2>

        {load.map((l) => (
          <div className="list-item" key={l.postazione}>
            <strong>{l.postazione}</strong>

            <div className="row-actions">
              <span className="badge neutral">tot {l.orders_total}</span>
              <span className="badge neutral">open {l.orders_open}</span>
              <span className="badge success">done {l.orders_done}</span>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}
