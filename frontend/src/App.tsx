import { FormEvent, useEffect, useMemo, useState } from 'react'
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

type EventCreatePayload = {
  title: string
  line: string
  station: string
  event_type: string
  severity: string
  note: string
  source: string
}

const API_BASE = '/api'

const initialForm: EventCreatePayload = {
  title: '',
  line: 'L1',
  station: 'ZAW2',
  event_type: 'CRIMPATURA',
  severity: 'CRITICAL',
  note: '',
  source: 'dashboard',
}

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
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState<string>('')

  const [form, setForm] = useState<EventCreatePayload>(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState('')

  async function loadData(showSpinner = false) {
    try {
      if (showSpinner) setLoading(true)
      setError('')

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
      if (showSpinner) setLoading(false)
    }
  }

  useEffect(() => {
    void loadData(true)

    const timer = window.setInterval(() => {
      void loadData(false)
    }, 5000)

    return () => window.clearInterval(timer)
  }, [])

  const openEvents = useMemo(
    () => events?.items.filter((item) => item.status === 'OPEN') ?? [],
    [events],
  )

  const closedEvents = useMemo(
    () => events?.items.filter((item) => item.status === 'CLOSED') ?? [],
    [events],
  )

  function updateForm<K extends keyof EventCreatePayload>(
    key: K,
    value: EventCreatePayload[K],
  ) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }))
  }

  async function handleCreateEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitMessage('')

    if (!form.title.trim()) {
      setSubmitMessage('Inserisci il titolo evento.')
      return
    }

    try {
      setSubmitting(true)

      const payload = {
        title: form.title.trim(),
        line: form.line.trim(),
        station: form.station.trim(),
        event_type: form.event_type.trim(),
        severity: form.severity.trim(),
        note: form.note.trim(),
        source: form.source.trim() || 'dashboard',
      }

      const response = await fetch(`${API_BASE}/events/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const body = await response.text()
        throw new Error(body || 'Creazione evento fallita')
      }

      setForm(initialForm)
      setSubmitMessage('Evento creato correttamente.')
      await loadData(false)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Errore creazione evento'
      setSubmitMessage(message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleCloseEvent(eventId: string) {
    try {
      setBusyId(eventId)
      setSubmitMessage('')

      const response = await fetch(`${API_BASE}/events/${eventId}/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ closed_by: 'dashboard' }),
      })

      if (!response.ok) {
        const body = await response.text()
        throw new Error(body || 'Chiusura evento fallita')
      }

      await loadData(false)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Errore chiusura evento'
      setError(message)
    } finally {
      setBusyId('')
    }
  }

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">PROMETEO</p>
          <h1>Dashboard CORE locale</h1>
          <p className="sub">
            Monitoraggio backend FastAPI e gestione eventi/stato
          </p>
        </div>

        <div className="actions">
          <button
            onClick={() => void loadData(true)}
            disabled={loading || submitting || !!busyId}
          >
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

      <section className="card">
        <h2>Crea evento</h2>

        <form className="event-form" onSubmit={handleCreateEvent}>
          <div className="form-grid form-grid-2">
            <label className="field">
              <span>Titolo</span>
              <input
                type="text"
                value={form.title}
                onChange={(e) => updateForm('title', e.target.value)}
                placeholder="Es. Crimpatura KO"
              />
            </label>

            <label className="field">
              <span>Linea</span>
              <input
                type="text"
                value={form.line}
                onChange={(e) => updateForm('line', e.target.value)}
                placeholder="Es. L1"
              />
            </label>

            <label className="field">
              <span>Postazione</span>
              <input
                type="text"
                value={form.station}
                onChange={(e) => updateForm('station', e.target.value)}
                placeholder="Es. ZAW2"
              />
            </label>

            <label className="field">
              <span>Tipo evento</span>
              <select
                value={form.event_type}
                onChange={(e) => updateForm('event_type', e.target.value)}
              >
                <option value="CRIMPATURA">CRIMPATURA</option>
                <option value="SALDATURA">SALDATURA</option>
                <option value="PRESSIONE">PRESSIONE</option>
                <option value="QUALITA">QUALITA</option>
                <option value="MATERIALE">MATERIALE</option>
                <option value="FERMO_LINEA">FERMO_LINEA</option>
              </select>
            </label>

            <label className="field">
              <span>Severità</span>
              <select
                value={form.severity}
                onChange={(e) => updateForm('severity', e.target.value)}
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </label>

            <label className="field">
              <span>Sorgente</span>
              <input
                type="text"
                value={form.source}
                onChange={(e) => updateForm('source', e.target.value)}
                placeholder="dashboard"
              />
            </label>
          </div>

          <label className="field">
            <span>Nota</span>
            <textarea
              rows={4}
              value={form.note}
              onChange={(e) => updateForm('note', e.target.value)}
              placeholder="Dettaglio evento"
            />
          </label>

          <div className="form-actions">
            <button type="submit" disabled={submitting || !!busyId}>
              {submitting ? 'Creazione...' : 'Crea evento'}
            </button>
            {submitMessage ? (
              <span className="form-message">{submitMessage}</span>
            ) : null}
          </div>
        </form>
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

                  <div className="row-actions">
                    <span className="badge danger">{item.severity}</span>
                    <button
                      className="secondary-btn"
                      onClick={() => void handleCloseEvent(item.id)}
                      disabled={busyId === item.id || submitting}
                    >
                      {busyId === item.id ? 'Chiusura...' : 'Chiudi'}
                    </button>
                  </div>
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
              {closedEvents.slice(0, 10).map((item) => (
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
