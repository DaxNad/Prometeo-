import { useEffect, useState } from "react";
import type { TLExplainItem } from "../types/tl";

export function useTLExplain() {
  const [items, setItems] = useState<TLExplainItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      try {
        setLoading(true);
        // endpoint compatibile; fallback se non esiste
        const res = await fetch("/production/explain?compact=true");
        if (!res.ok) {
          setItems([]);
        } else {
          const data = await res.json();
          setItems(Array.isArray(data.items) ? data.items : []);
        }
      } catch (e) {
        if (!cancelled) setError("explain non disponibile");
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

