import { useEffect, useMemo, useState } from 'react'
import './App.css'

type HealthResponse = {
  ok: boolean
  service: string
  version: string
  ui_available: boolean
  database_configured: boolean
}

type EventItem = {
  id: string
  title: string
  line: string
  station: string
  event_type: string
  severity: string
  status: string
  note?: string
  source?: string
  opened_at?: string
  closed_at?: string | null
  closed_by?: string | null
}

type EventsResponse = {
  total: number
  open_count?: number
  closed_count?: number
  items: EventItem[]
}

type StateItem = {
  line: string
  station: string
  status?: string
  updated_at?: string
  note?: string
}

type StateResponse = {
  total: number
  items: StateItem[]
}

const API_BASE = 'http://127.0.0.1:8000'

function formatDate(value?: string | null) {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleString('it-IT')
  } catch {
    return value
  }
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [events, setEvents] = useState<EventsResponse | null>(null)
  const [state, setState] = useState<StateResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  async function loadData() {
    try {
      setError('')
      setLoading(true)

      const [healthRes, eventsRes, stateRes] = await Promise.all([
        fetch(`${API_BASE}/health`),
        fetch(`${API_BASE}/events`),
        fetch(`${API_BASE}/state`),
      ])

      if (!healthRes.ok) throw new Error('health non disponibile')
      if (!eventsRes.ok) throw new Error('events non disponibile')
      if (!stateRes.ok) throw new Error('state non disponibile')

      const healthJson: HealthResponse = await healthRes.json()
      const eventsJson: EventsResponse = await eventsRes.json()
      const stateJson: StateResponse = await stateRes.json()

      setHealth(healthJson)
      setEvents(eventsJson)
      setState(stateJson)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Errore caricamento dati'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadData()
    const timer = window.setInterval(() => {
      void loadData()
    }, 10000)

    return () => window.clearInterval(timer)
  }, [])

  const openEvents = useMemo(() => {
    return events?.items.filter((item) => item.status === 'OPEN') ?? []
  }, [events])

  const closedEvents = useMemo(() => {
    return events?.items.filter((item) => item.status === 'CLOSED') ?? []
  }, [events])

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">PROMETEO</p>
          <h1>Dashboard CORE locale</h1>
          <p className="sub">
            Monitoraggio backend FastAPI e dati eventi/stato
          </p>
        </div>

        <div className="actions">
          <button onClick={() => void loadData()} disabled={loading}>
            {loading ? 'Aggiornamento...' : 'Aggiorna'}
          </button>
        </div>
      </header>

      {error ? <div className="alert error">Errore: {error}</div> : null}

      <section className="grid grid-4">
        <article className="card stat">
          <span className="label">Servizio</span>
          <strong>{health?.service ?? '—'}</strong>
        </article>

        <article className="card stat">
          <span className="label">Versione</span>
          <strong>{health?.version ?? '—'}</strong>
        </article>

        <article className="card stat">
          <span className="label">Eventi totali</span>
          <strong>{events?.total ?? 0}</strong>
        </article>

        <article className="card stat">
          <span className="label">Stati postazione</span>
          <strong>{state?.total ?? 0}</strong>
        </article>
      </section>

      <section className="grid grid-2">
        <article className="card">
          <h2>Stato sistema</h2>
          <div className="kv">
            <span>Backend</span>
            <strong>{health?.ok ? 'ONLINE' : 'OFFLINE'}</strong>
          </div>
          <div className="kv">
            <span>UI disponibile</span>
            <strong>{health?.ui_available ? 'SI' : 'NO'}</strong>
          </div>
          <div className="kv">
            <span>Database configurato</span>
            <strong>{health?.database_configured ? 'SI' : 'NO'}</strong>
          </div>
        </article>

        <article className="card">
          <h2>Riepilogo eventi</h2>
          <div className="kv">
            <span>Aperti</span>
            <strong>{openEvents.length}</strong>
          </div>
          <div className="kv">
            <span>Chiusi</span>
            <strong>{closedEvents.length}</strong>
          </div>
          <div className="kv">
            <span>Ultimo refresh</span>
            <strong>{new Date().toLocaleTimeString('it-IT')}</strong>
          </div>
        </article>
      </section>

      <section className="grid grid-2">
        <article className="card">
          <h2>Eventi aperti</h2>
          {openEvents.length === 0 ? (
            <p className="empty">Nessun evento aperto.</p>
          ) : (
            <div className="list">
              {openEvents.map((item) => (
                <div className="list-item" key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <p>
                      {item.line} · {item.station} · {item.event_type}
                    </p>
                  </div>
                  <span className="badge danger">{item.severity}</span>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="card">
          <h2>Ultimi eventi chiusi</h2>
          {closedEvents.length === 0 ? (
            <p className="empty">Nessun evento chiuso.</p>
          ) : (
            <div className="list">
              {closedEvents.slice(0, 5).map((item) => (
                <div className="list-item" key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <p>
                      {item.line} · {item.station} · chiuso:{' '}
                      {formatDate(item.closed_at)}
                    </p>
                  </div>
                  <span className="badge success">{item.status}</span>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>

      <section className="card">
        <h2>Stato postazioni</h2>
        {state?.items?.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Linea</th>
                  <th>Postazione</th>
                  <th>Stato</th>
                  <th>Nota</th>
                  <th>Aggiornato</th>
                </tr>
              </thead>
              <tbody>
                {state.items.map((row, index) => (
                  <tr key={`${row.line}-${row.station}-${index}`}>
                    <td>{row.line}</td>
                    <td>{row.station}</td>
                    <td>{row.status ?? '—'}</td>
                    <td>{row.note ?? '—'}</td>
                    <td>{formatDate(row.updated_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="empty">Nessuno stato disponibile.</p>
        )}
      </section>
    </div>
  )
}

export default App
