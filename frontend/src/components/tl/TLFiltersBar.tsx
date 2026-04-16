interface Props {
  station: string;
  setStation: (v: string) => void;
  risk: string;
  setRisk: (v: string) => void;
  onlyEvent: boolean;
  setOnlyEvent: (v: boolean) => void;
  onlyBlocked: boolean;
  setOnlyBlocked: (v: boolean) => void;
  query: string;
  setQuery: (v: string) => void;
  stations: string[];
}

export default function TLFiltersBar(p: Props) {
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
      <label>
        <span style={{ marginRight: 6 }}>stazione</span>
        <select value={p.station} onChange={(e) => p.setStation(e.target.value)}>
          <option value="ALL">tutte</option>
          {p.stations.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>

      <label>
        <span style={{ marginRight: 6 }}>rischio</span>
        <select value={p.risk} onChange={(e) => p.setRisk(e.target.value)}>
          <option value="ALL">tutti</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </label>

      <label style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
        <input type="checkbox" checked={p.onlyEvent} onChange={(e) => p.setOnlyEvent(e.target.checked)} />
        <span>solo event_impact</span>
      </label>

      <label style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
        <input type="checkbox" checked={p.onlyBlocked} onChange={(e) => p.setOnlyBlocked(e.target.checked)} />
        <span>solo bloccati</span>
      </label>

      <input
        value={p.query}
        onChange={(e) => p.setQuery(e.target.value)}
        placeholder="cerca articolo/ordine"
        style={{ padding: 6, borderRadius: 6, border: "1px solid #333", background: "#111", color: "#fff" }}
      />
    </div>
  );
}

