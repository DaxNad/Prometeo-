export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | string;

// Contratto dati stabile per le righe TL Board
export interface TLSequenceItem {
  // ranking e identità
  rank?: number;
  article_code?: string; // alias di "article" / "code" lato backend
  order_id?: string;

  // segnali principali
  critical_station?: string;
  customer_priority?: string; // es. ALTA/MEDIA/BASSA
  risk_level?: RiskLevel;
  event_impact?: boolean;
  open_events_total?: number; // opzionale: può provenire da machine-load

  // motivazioni leggibili lato TL
  priority_reason?: string;
  suggested_action?: string;

  // eventuali altri campi grezzi
  quantity?: number;
}

export interface TLExplainItem {
  article?: string; // per compat
  order_id?: string;
  risk_level?: RiskLevel;
  // explain compatto (se disponibile): elenco motivi già raggruppabili
  reasons?: string[];
  // campi sintetici per pannello dettaglio
  priority_reason?: string;
  suggested_action?: string;
}

export interface TLMachineLoadItem {
  station?: string;
  orders_total?: number;
  red_total?: number;
  yellow_total?: number;
  green_total?: number;
  open_events_total?: number;
}
