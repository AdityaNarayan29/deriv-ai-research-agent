/**
 * Client-side demo simulator — plays back demo data with intentional
 * loading delays so the UI feels like a real investigation, even when
 * the backend is completely unreachable.
 *
 * Emits the same SSEEvent shapes that the real backend SSE stream produces.
 */

import type { SSEEvent } from "./types";
import {
  DEMO_TARGET_NAME,
  DEMO_TARGET_CONTEXT,
  DEMO_FACTS,
  DEMO_ENTITIES,
  DEMO_RISK_FLAGS,
  DEMO_REPORT,
  DEMO_EXECUTION_LOG,
  DEMO_PIPELINE_STEPS,
} from "./demoData";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/**
 * Simulate a full investigation by emitting SSEEvents to the callback
 * with realistic timing. Runs entirely in the browser — zero network calls.
 */
export async function runDemoLocally(
  onEvent: (event: SSEEvent) => void
): Promise<void> {
  const logsPerStep = Math.floor(
    DEMO_EXECUTION_LOG.length / DEMO_PIPELINE_STEPS.length
  );
  let logIdx = 0;

  for (let i = 0; i < DEMO_PIPELINE_STEPS.length; i++) {
    const [node, iteration, progress] = DEMO_PIPELINE_STEPS[i];

    // node_start event
    onEvent({
      type: "node_start",
      node,
      iteration,
      progress,
    });
    await sleep(350);

    // Send log lines for this step
    const stepEnd = Math.min(logIdx + logsPerStep + 1, DEMO_EXECUTION_LOG.length);
    for (let j = logIdx; j < stepEnd; j++) {
      onEvent({ type: "log", message: DEMO_EXECUTION_LOG[j] });
      await sleep(120);
    }
    logIdx = stepEnd;

    // Send data updates at appropriate pipeline stages
    if (node === "fact_extractor" && iteration === 0) {
      onEvent({
        type: "facts_update",
        facts: DEMO_FACTS.slice(0, 15),
        total: 15,
      });
      onEvent({
        type: "entities_update",
        entities: DEMO_ENTITIES.slice(0, 10),
        total: 10,
      });
    } else if (node === "fact_extractor" && iteration === 1) {
      onEvent({
        type: "facts_update",
        facts: DEMO_FACTS.slice(15, 33),
        total: 33,
      });
      onEvent({
        type: "entities_update",
        entities: DEMO_ENTITIES.slice(10, 18),
        total: 18,
      });
    } else if (node === "fact_extractor" && iteration === 2) {
      onEvent({
        type: "facts_update",
        facts: DEMO_FACTS.slice(33),
        total: DEMO_FACTS.length,
      });
      onEvent({
        type: "entities_update",
        entities: DEMO_ENTITIES.slice(18),
        total: DEMO_ENTITIES.length,
      });
    } else if (node === "risk_analyzer" && iteration === 0) {
      onEvent({
        type: "risks_update",
        risk_flags: DEMO_RISK_FLAGS.slice(0, 4),
        total: 4,
      });
    } else if (node === "risk_analyzer" && iteration === 1) {
      onEvent({
        type: "risks_update",
        risk_flags: DEMO_RISK_FLAGS.slice(4, 7),
        total: 7,
      });
    } else if (node === "risk_analyzer" && iteration === 2) {
      onEvent({
        type: "risks_update",
        risk_flags: DEMO_RISK_FLAGS.slice(7),
        total: DEMO_RISK_FLAGS.length,
      });
    }

    await sleep(250);
  }

  // Flush remaining log lines
  for (let j = logIdx; j < DEMO_EXECUTION_LOG.length; j++) {
    onEvent({ type: "log", message: DEMO_EXECUTION_LOG[j] });
    await sleep(80);
  }

  // Final complete event
  onEvent({
    type: "complete",
    result: {
      id: `demo-${Date.now()}`,
      target_name: DEMO_TARGET_NAME,
      target_context: DEMO_TARGET_CONTEXT,
      facts: DEMO_FACTS,
      entities: DEMO_ENTITIES,
      risk_flags: DEMO_RISK_FLAGS,
      report: DEMO_REPORT,
      graph_html: "",
      iteration: 3,
      execution_log: DEMO_EXECUTION_LOG,
    },
  });
}
