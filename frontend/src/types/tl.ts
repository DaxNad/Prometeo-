export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | string;

export interface TLSequenceItem {
  rank?: number;
  article?: string;
  order_id?: string;
  critical_station?: string;
  customer_priority?: string;
  event_impact?: boolean;
  quantity?: number;
}

export interface TLExplainItem {
  article?: string;
  order_id?: string;
  risk_level?: RiskLevel;
  reasons?: string[];
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

