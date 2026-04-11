import { EntityType } from "./types";

export const ENTITY_CONFIG: Record<
  EntityType,
  {
    color: string;
    borderColor: string;
    highlightColor: string;
    label: string;
  }
> = {
  [EntityType.PERSON]: {
    color: "#6366f1",
    borderColor: "#4f46e5",
    highlightColor: "#818cf8",
    label: "Person",
  },
  [EntityType.ORGANIZATION]: {
    color: "#f59e0b",
    borderColor: "#d97706",
    highlightColor: "#fbbf24",
    label: "Organization",
  },
  [EntityType.EVENT]: {
    color: "#10b981",
    borderColor: "#059669",
    highlightColor: "#34d399",
    label: "Event",
  },
  [EntityType.FILING]: {
    color: "#8b5cf6",
    borderColor: "#7c3aed",
    highlightColor: "#a78bfa",
    label: "Filing",
  },
  [EntityType.LOCATION]: {
    color: "#ef4444",
    borderColor: "#dc2626",
    highlightColor: "#f87171",
    label: "Location",
  },
};

export const TARGET_COLOR = "#ef4444";
export const TARGET_BORDER = "#fbbf24";

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "#22c55e";
  if (confidence >= 0.5) return "#eab308";
  return "#ef4444";
}

export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return "High";
  if (confidence >= 0.5) return "Medium";
  return "Low";
}

export function getSeverityColor(severity: number): string {
  const colors: Record<number, string> = {
    1: "#64748b",
    2: "#eab308",
    3: "#f97316",
    4: "#ef4444",
    5: "#dc2626",
  };
  return colors[severity] || "#64748b";
}

export const PIPELINE_NODES = [
  { key: "query_planner", label: "Query Planner" },
  { key: "search_executor", label: "Search" },
  { key: "fact_extractor", label: "Fact Extractor" },
  { key: "risk_analyzer", label: "Risk Analyzer" },
  { key: "query_refiner", label: "Query Refiner" },
  { key: "graph_builder", label: "Graph Builder" },
  { key: "report_generator", label: "Report Generator" },
];
