import { useEffect, useState } from "react";
import type { TLSequenceItem } from "../types/tl";

export function useTLSequence() {
  const [items, setItems] = useState<TLSequenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      try {
        setLoading(true);
        const res = await fetch("/production/sequence");
        if (!res.ok) throw new Error("network");
        const data = await res.json();
        const raw: any[] = Array.isArray(data.items) ? data.items : [];
        const mapped: TLSequenceItem[] = raw.map((it, idx) => ({
          rank: it.rank ?? idx + 1,
          article_code: it.article ?? it.code ?? it.codice ?? undefined,
          order_id: it.order_id ?? undefined,
          critical_station: it.critical_station ?? it.criticalStation ?? it.station ?? undefined,
          customer_priority: it.customer_priority ?? it.priority ?? undefined,
          risk_level: it.risk_level ?? undefined,
          event_impact: Boolean(it.event_impact),
          open_events_total: it.open_events_total ?? undefined,
          priority_reason: it.priority_reason ?? undefined,
          suggested_action: it.suggested_action ?? undefined,
          quantity: it.quantity ?? it.qta ?? undefined,
        }));
        if (!cancelled) setItems(mapped);
      } catch (e) {
        if (!cancelled) setError("impossibile caricare la sequenza");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, []);

  return { items, loading, error };
}
