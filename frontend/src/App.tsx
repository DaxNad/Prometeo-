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
  severity?: string | null
  event_type?: string | null
  title?: string | null
  note?: string
  source?: string | null
  event_id?: string | null
  updated_at?: string
  priority_score?: number
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
  const [busyId, setBusyId] = useState('')
  const [busyLine, setBusyLine] = useState('')

  const [form, setForm] = useState<EventCreatePayload>(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState('')

  const [filterLine, setFilterLine] = useState('ALL')
  const [filterStation, setFilterStation] = useState('ALL')
  const [filterSeverity, setFilterSeverity] = useState('ALL')
  const [filterOnlyOpen, setFilterOnlyOpen] = useState(false)

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

  const allLines = useMemo(() => {
    const values = new Set<string>()
    ;(events?.items ?? []).forEach((item) => values.add(item.line))
    ;(state?.items ?? []).forEach((item) => item.line && values.add(item.line))
    return ['ALL', ...Array.from(values).sort()]
  }, [events, state])

  const allStations = useMemo(() => {
    const values = new Set<string>()
    ;(events?.items ?? []).forEach((item) => values.add(item.station))
    ;(state?.items ?? []).forEach((item) => item.station && values.add(item.station))
    return ['ALL', ...Array.from(values).sort()]
  }, [events, state])

  function matchCommonFilters(item: {
    line?: string
    station?: string
    severity?: string | null
    status?: string
  }) {
    const lineOk = filterLine === 'ALL' || item.line === filterLine
    const stationOk = filterStation === 'ALL' || item.station === filterStation
    const severityOk =
      filterSeverity === 'ALL' || item.severity === filterSeverity
    const openOk = !filterOnlyOpen || item.status === 'OPEN'

    return lineOk && stationOk && severityOk && openOk
  }

  const openEvents = useMemo(() => {
    return (events?.items ?? []).filter(
      (item) => item.status === 'OPEN' && matchCommonFilters(item),
    )
  }, [events, filterLine, filterStation, filterSeverity, filterOnlyOpen])

  const closedEvents = useMemo(() => {
    return (events?.items ?? []).filter(
      (item) => item.status === 'CLOSED' && matchCommonFilters(item),
    )
  }, [events, filterLine, filterStation, filterSeverity, filterOnlyOpen])

  const priorityStations = useMemo(() => {
    return [...(state?.items ?? [])].filter((item) => matchCommonFilters(item))
  }, [state, filterLine, filterStation, filterSeverity, filterOnlyOpen])

  const criticalOpenCount = useMemo(() => {
    return openEvents.filter((item) => item.severity === 'CRITICAL').length
  }, [openEvents])

  const highOpenCount = useMemo(() => {
    return openEvents.filter((item) => item.severity === 'HIGH').length
  }, [openEvents])

  const activeLines = useMemo(() => {
    return new Set(openEvents.map((item) => item.line)).size
  }, [openEvents])

  const activeStations = useMemo(() => {
    return new Set(openEvents.map((item) => `${item.line}__${item.station}`)).size
  }, [openEvents])

  const lineCounters = useMemo(() => {
    const counters = new Map<
      string,
      { total: number; critical: number; high: number; open: number }
    >()

    openEvents.forEach((item) => {
      const current = counters.get(item.line) ?? {
        total: 0,
        critical: 0,
        high: 0,
        open: 0,
      }

      current.total += 1
      current.open += 1
      if (item.severity === 'CRITICAL') current.critical += 1
      if (item.severity === 'HIGH') current.high += 1

      counters.set(item.line, current)
    })

    return Array.from(counters.entries())
      .map(([line, values]) => ({ line, ...values }))
      .sort((a, b) => {
        if (b.critical !== a.critical) return b.critical - a.critical
        if (b.high !== a.high) return b.high - a.high
        return b.open - a.open
      })
  }, [openEvents])

  const topCriticalNow = useMemo(() => {
    return priorityStations
      .filter((item) => item.status === 'OPEN' && item.severity === 'CRITICAL')
      .slice(0, 5)
  }, [priorityStations])

  const topAbsolutePriorities = useMemo(() => {
    return [...priorityStations]
      .sort((a, b) => (b.priority_score ?? 0) - (a.priority_score ?? 0))
      .slice(0, 5)
  }, [priorityStations])

  const repartoSummary = useMemo(() => {
    const map = new Map<
      string,
      {
        line: string
        open: number
        closed: number
        critical: number
        high: number
        stations: Set<string>
      }
    >()

    ;(events?.items ?? []).forEach((item) => {
      const current = map.get(item.line) ?? {
        line: item.line,
        open: 0,
        closed: 0,
        critical: 0,
        high: 0,
        stations: new Set<string>(),
      }

      current.stations.add(item.station)
      if (item.status === 'OPEN') current.open += 1
      if (item.status === 'CLOSED') current.closed += 1
      if (item.status === 'OPEN' && item.severity === 'CRITICAL') current.critical += 1
      if (item.status === 'OPEN' && item.severity === 'HIGH') current.high += 1

      map.set(item.line, current)
    })

    return Array.from(map.values())
      .map((row) => ({
        ...row,
        stationsCount: row.stations.size,
      }))
      .sort((a, b) => {
        if (b.critical !== a.critical) return b.critical - a.critical
        if (b.open !== a.open) return b.open - a.open
        return a.line.localeCompare(b.line)
      })
  }, [events])

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
        headers: { 'Content-Type': 'application/json' },
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
        headers: { 'Content-Type': 'application/json' },
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

  async function handleCloseByLine(line: string) {
    try {
      setBusyLine(line)
      setSubmitMessage('')

      const response = await fetch(`${API_BASE}/events/close-by-line`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ line, closed_by: 'dashboard-line' }),
      })

      if (!response.ok) {
        const body = await response.text()
        throw new Error(body || 'Chiusura massiva fallita')
      }

      await loadData(false)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Errore chiusura linea'
      setError(message)
    } finally {
      setBusyLine('')
    }
  }

  function resetFilters() {
    setFilterLine('ALL')
    setFilterStation('ALL')
    setFilterSeverity('ALL')
    setFilterOnlyOpen(false)
  }

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">PROMETEO</p>
          <h1>Dashboard CORE locale</h1>
          <p className="sub">
            Monitoraggio backend FastAPI, priorità postazioni e gestione eventi
          </p>
        </div>

        <div className="actions">
          <button
            onClick={() => void loadData(true)}
            disabled={loading || submitting || !!busyId || !!busyLine}
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
          <span className="label">Eventi totali filtrati</span>
          <strong>{openEvents.length + closedEvents.length}</strong>
        </article>

        <article className="card stat">
          <span className="label">Stati postazione filtrati</span>
          <strong>{priorityStations.length}</strong>
        </article>
      </section>

      <section className="grid grid-4">
        <article className="card kpi-card">
          <span className="label">Aperti</span>
          <strong>{openEvents.length}</strong>
        </article>

        <article className="card kpi-card kpi-critical">
          <span className="label">Critici aperti</span>
          <strong>{criticalOpenCount}</strong>
        </article>

        <article className="card kpi-card kpi-high">
          <span className="label">High aperti</span>
          <strong>{highOpenCount}</strong>
        </article>

        <article className="card kpi-card">
          <span className="label">Linee / Postazioni</span>
          <strong>
            {activeLines} / {activeStations}
          </strong>
        </article>
      </section>

      <section className="grid grid-2">
        <article className="card critical-panel">
          <h2>Criticità immediate</h2>
          {topCriticalNow.length === 0 ? (
            <p className="empty">Nessuna criticità CRITICAL aperta.</p>
          ) : (
            <div className="list">
              {topCriticalNow.map((item, index) => (
                <div className="list-item highlight-item" key={`${item.event_id}-${index}`}>
                  <div>
                    <strong>
                      {item.line} · {item.station} · {item.title ?? '—'}
                    </strong>
                    <p>
                      {item.event_type ?? '—'} · {item.severity ?? '—'} · priorità{' '}
                      {item.priority_score ?? 0}
                    </p>
                    <p>
                      nota: {item.note || '—'} · aggiornato: {formatDate(item.updated_at)}
                    </p>
                  </div>
                  <span className="badge danger">CRITICAL</span>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="card">
          <h2>Top 5 priorità assolute</h2>
          {topAbsolutePriorities.length === 0 ? (
            <p className="empty">Nessuna priorità disponibile.</p>
          ) : (
            <div className="list">
              {topAbsolutePriorities.map((item, index) => (
                <div className="list-item" key={`${item.event_id}-${index}`}>
                  <div>
                    <strong>
                      #{index + 1} · {item.line} · {item.station}
                    </strong>
                    <p>
                      {item.title ?? '—'} · {item.event_type ?? '—'} ·{' '}
                      {item.severity ?? '—'}
                    </p>
                  </div>
                  <div className="row-actions">
                    <span
                      className={
                        item.status === 'OPEN' ? 'badge danger' : 'badge success'
                      }
                    >
                      {item.status ?? '—'}
                    </span>
                    <span className="badge neutral">
                      P {item.priority_score ?? 0}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>

      <section className="card">
        <h2>Riepilogo reparto per linea</h2>
        {repartoSummary.length === 0 ? (
          <p className="empty">Nessun dato reparto disponibile.</p>
        ) : (
          <div className="list">
            {repartoSummary.map((row) => (
              <div className="list-item" key={row.line}>
                <div>
                  <strong>{row.line}</strong>
                  <p>
                    OPEN {row.open} · CLOSED {row.closed} · CRITICAL {row.critical} ·
                    HIGH {row.high} · POSTAZIONI {row.stationsCount}
                  </p>
                </div>
                <div className="row-actions">
                  <span className="badge neutral">LINEA</span>
                  <button
                    className="secondary-btn"
                    onClick={() => void handleCloseByLine(row.line)}
                    disabled={busyLine === row.line || row.open === 0 || submitting || !!busyId}
                  >
                    {busyLine === row.line ? 'Chiusura linea...' : 'Chiudi tutti OPEN'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
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
          <h2>Riepilogo filtrato</h2>
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
        <h2>Badge linea</h2>
        {lineCounters.length === 0 ? (
          <p className="empty">Nessuna linea con eventi aperti.</p>
        ) : (
          <div className="line-badges">
            {lineCounters.map((item) => (
              <div className="line-badge" key={item.line}>
                <strong>{item.line}</strong>
                <span>OPEN {item.open}</span>
                <span>CRITICAL {item.critical}</span>
                <span>HIGH {item.high}</span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="card">
        <h2>Filtri operativi</h2>

        <div className="form-grid form-grid-4">
          <label className="field">
            <span>Linea</span>
            <select
              value={filterLine}
              onChange={(e) => setFilterLine(e.target.value)}
            >
              {allLines.map((value) => (
                <option key={value} value={value}>
                  {value === 'ALL' ? 'TUTTE' : value}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Postazione</span>
            <select
              value={filterStation}
              onChange={(e) => setFilterStation(e.target.value)}
            >
              {allStations.map((value) => (
                <option key={value} value={value}>
                  {value === 'ALL' ? 'TUTTE' : value}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Severità</span>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
            >
              <option value="ALL">TUTTE</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </label>

          <label className="field checkbox-field">
            <span>Solo OPEN</span>
            <input
              type="checkbox"
              checked={filterOnlyOpen}
              onChange={(e) => setFilterOnlyOpen(e.target.checked)}
            />
          </label>
        </div>

        <div className="form-actions">
          <button className="secondary-btn" onClick={resetFilters}>
            Reset filtri
          </button>
        </div>
      </section>

      <section className="card">
        <h2>Priorità postazioni</h2>
        {priorityStations.length === 0 ? (
          <p className="empty">Nessuna postazione disponibile con i filtri attivi.</p>
        ) : (
          <div className="list">
            {priorityStations.map((row, index) => (
              <div className="list-item" key={`${row.line}-${row.station}-${index}`}>
                <div>
                  <strong>
                    {row.line} · {row.station} · {row.status ?? '—'}
                  </strong>
                  <p>
                    {row.title ?? '—'} · {row.event_type ?? '—'} ·{' '}
                    {row.severity ?? '—'} · priorità {row.priority_score ?? 0}
                  </p>
                  <p>
                    nota: {row.note || '—'} · aggiornato: {formatDate(row.updated_at)}
                  </p>
                </div>
                <div className="row-actions">
                  <span
                    className={
                      row.status === 'OPEN' ? 'badge danger' : 'badge success'
                    }
                  >
                    {row.status ?? '—'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
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
            <button type="submit" disabled={submitting || !!busyId || !!busyLine}>
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
            <p className="empty">Nessun evento aperto con i filtri attivi.</p>
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
                      disabled={busyId === item.id || submitting || !!busyLine}
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
          <h2>Eventi chiusi</h2>
          {closedEvents.length === 0 ? (
            <p className="empty">Nessun evento chiuso con i filtri attivi.</p>
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
    </div>
  )
}

export default App
