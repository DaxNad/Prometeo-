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

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">PROMETEO</p>
          <h1>Dashboard Produzione</h1>
        </div>

        <button onClick={loadData}>aggiorna</button>
      </header>

      <section className="card">
        <h2>Board ordini</h2>

        {loading && <p>caricamento...</p>}

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
