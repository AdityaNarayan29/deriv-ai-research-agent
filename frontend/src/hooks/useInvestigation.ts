"use client";

import { useReducer, useCallback } from "react";
import { startInvestigation } from "@/lib/api";
import type { ExtractedFact, Entity, RiskFlag, SSEEvent } from "@/lib/types";

export type InvestigationStatus = "idle" | "running" | "complete" | "error";

export interface InvestigationState {
  status: InvestigationStatus;
  currentNode: string;
  progress: number;
  iteration: number;
  logs: string[];
  facts: ExtractedFact[];
  entities: Entity[];
  riskFlags: RiskFlag[];
  report: string;
  graphHtml: string;
  error: string | null;
  investigationId: string | null;
}

type Action =
  | { type: "START" }
  | { type: "SSE_EVENT"; event: SSEEvent }
  | { type: "ERROR"; error: string };

const initialState: InvestigationState = {
  status: "idle",
  currentNode: "",
  progress: 0,
  iteration: 0,
  logs: [],
  facts: [],
  entities: [],
  riskFlags: [],
  report: "",
  graphHtml: "",
  error: null,
  investigationId: null,
};

function reducer(state: InvestigationState, action: Action): InvestigationState {
  switch (action.type) {
    case "START":
      return { ...initialState, status: "running" };

    case "SSE_EVENT": {
      const event = action.event;
      switch (event.type) {
        case "node_start":
          return {
            ...state,
            currentNode: event.node,
            progress: event.progress,
            iteration: event.iteration,
          };

        case "log":
          return {
            ...state,
            logs: [...state.logs, event.message],
          };

        case "facts_update":
          return {
            ...state,
            facts: deduplicateById([...state.facts, ...event.facts]),
          };

        case "entities_update":
          return {
            ...state,
            entities: deduplicateById([...state.entities, ...event.entities]),
          };

        case "risks_update":
          return {
            ...state,
            riskFlags: deduplicateById([
              ...state.riskFlags,
              ...event.risk_flags,
            ]),
          };

        case "complete":
          return {
            ...state,
            status: "complete",
            progress: 1,
            currentNode: "",
            facts: event.result.facts,
            entities: event.result.entities,
            riskFlags: event.result.risk_flags,
            report: event.result.report,
            graphHtml: event.result.graph_html,
            investigationId: event.result.id,
            logs: event.result.execution_log,
          };

        case "error":
          return {
            ...state,
            status: "error",
            error: event.message,
          };

        default:
          return state;
      }
    }

    case "ERROR":
      return { ...state, status: "error", error: action.error };

    default:
      return state;
  }
}

function deduplicateById<T extends { id: string }>(items: T[]): T[] {
  const seen = new Set<string>();
  return items.filter((item) => {
    if (seen.has(item.id)) return false;
    seen.add(item.id);
    return true;
  });
}

export function useInvestigation() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const start = useCallback(
    async (
      targetName: string,
      targetContext: string,
      maxIterations: number
    ) => {
      dispatch({ type: "START" });
      try {
        await startInvestigation(
          targetName,
          targetContext,
          maxIterations,
          (event) => dispatch({ type: "SSE_EVENT", event })
        );
      } catch (err) {
        dispatch({ type: "ERROR", error: (err as Error).message });
      }
    },
    []
  );

  return { ...state, start };
}
