// Mirrors agent/state.py exactly

export enum EntityType {
  PERSON = "person",
  ORGANIZATION = "organization",
  EVENT = "event",
  FILING = "filing",
  LOCATION = "location",
}

export enum FactCategory {
  BIOGRAPHICAL = "biographical",
  PROFESSIONAL = "professional",
  FINANCIAL = "financial",
  LEGAL = "legal",
  SOCIAL = "social",
  REGULATORY = "regulatory",
}

export enum RiskCategory {
  REGULATORY = "regulatory",
  REPUTATIONAL = "reputational",
  FINANCIAL = "financial",
  LEGAL = "legal",
  INCONSISTENCY = "inconsistency",
}

export enum RiskSeverity {
  LOW = 1,
  MODERATE = 2,
  ELEVATED = 3,
  HIGH = 4,
  CRITICAL = 5,
}

export interface ExtractedFact {
  id: string;
  subject: string;
  predicate: string;
  object: string;
  source_url: string;
  confidence: number;
  category: FactCategory;
  source_query: string;
}

export interface Entity {
  id: string;
  name: string;
  entity_type: EntityType;
  description: string;
  first_seen_query: string;
  investigated: boolean;
}

export interface RiskFlag {
  id: string;
  description: string;
  severity: RiskSeverity;
  category: RiskCategory;
  evidence_fact_ids: string[];
  recommendation: string;
}

export interface InvestigationResult {
  id: string;
  target_name: string;
  target_context: string;
  facts: ExtractedFact[];
  entities: Entity[];
  risk_flags: RiskFlag[];
  report: string;
  graph_html: string;
  iteration: number;
  execution_log: string[];
}

export type SSEEvent =
  | { type: "node_start"; node: string; iteration: number; progress: number }
  | { type: "log"; message: string }
  | { type: "facts_update"; facts: ExtractedFact[]; total: number }
  | { type: "entities_update"; entities: Entity[]; total: number }
  | { type: "risks_update"; risk_flags: RiskFlag[]; total: number }
  | { type: "complete"; result: InvestigationResult }
  | { type: "error"; message: string };
