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
        if (!cancelled) setItems(Array.isArray(data.items) ? data.items : []);
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

