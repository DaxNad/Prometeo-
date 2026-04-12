export type Stato = "da fare" | "in corso" | "finito" | "bloccato";
export type Semaforo = "VERDE" | "GIALLO" | "ROSSO";

export type BoardItem = {
  order_id: string;
  cliente: string;
  codice: string;
  qta: number;
  postazione: string;
  stato: Stato;
  progress: number;
  semaforo: Semaforo;
  due_date: string;
  note: string;
  updated_at: string;
};

export type BoardResponse = {
  ok: boolean;
  count: number;
  items: BoardItem[];
};
