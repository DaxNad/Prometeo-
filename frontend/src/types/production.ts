export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export type GenericApiResponse = Record<string, JsonValue>;

export interface ProductionBoardResponse extends GenericApiResponse {}
export interface ProductionDelaysResponse extends GenericApiResponse {}
export interface ProductionLoadResponse extends GenericApiResponse {}
export interface ProductionSequenceResponse extends GenericApiResponse {}
export interface ProductionTurnPlanResponse extends GenericApiResponse {}
