import { useMemo, useState } from "react";
import TLBoardHeader from "../components/tl/TLBoardHeader";
import TLSummaryCards from "../components/tl/TLSummaryCards";
import TLMachineLoadPanel from "../components/tl/TLMachineLoadPanel";
import TLSequenceTable from "../components/tl/TLSequenceTable";
import TLDetailPanel from "../components/tl/TLDetailPanel";
import TLFiltersBar from "../components/tl/TLFiltersBar";
import { useTLSequence } from "../hooks/useTLSequence";
import { useTLMachineLoad } from "../hooks/useTLMachineLoad";
import { useTLExplain } from "../hooks/useTLExplain";
import type { TLSequenceItem } from "../types/tl";

export default function TLBoardPage() {
  const { items: seq, loading: lSeq } = useTLSequence();
  const { items: load } = useTLMachineLoad();
  const { items: explain } = useTLExplain();

  const [station, setStation] = useState("ALL");
  const [risk, setRisk] = useState("ALL");
  const [onlyEvent, setOnlyEvent] = useState(false);
  const [onlyBlocked, setOnlyBlocked] = useState(false);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<TLSequenceItem | null>(null);

  const stations = useMemo(() => Array.from(new Set((seq || []).map(i => i.critical_station).filter(Boolean))) as string[], [seq]);

  const filters = { station, risk, onlyEvent, onlyBlocked, query };

  return (
    <main style={{ padding: 16, display: "grid", gap: 12, maxWidth: 1200, margin: "0 auto" }}>
      <TLBoardHeader />
      <TLSummaryCards load={load} />
      <TLFiltersBar
        station={station}
        setStation={setStation}
        risk={risk}
        setRisk={setRisk}
        onlyEvent={onlyEvent}
        setOnlyEvent={setOnlyEvent}
        onlyBlocked={onlyBlocked}
        setOnlyBlocked={setOnlyBlocked}
        query={query}
        setQuery={setQuery}
        stations={stations}
      />

      <section style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 12 }}>
        <div>
          {lSeq ? (
            <div style={{ padding: 12 }}>caricamento…</div>
          ) : (
            <TLSequenceTable items={seq} onSelect={setSelected} filters={filters} />
          )}
        </div>
        <div style={{ display: "grid", gap: 12 }}>
          <TLMachineLoadPanel items={load} />
          <TLDetailPanel item={selected} explain={explain} />
        </div>
      </section>
    </main>
  );
}

