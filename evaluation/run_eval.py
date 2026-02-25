"""Evaluation runner — executes the agent on all 3 test personas and produces metrics."""

import os
import sys
import json
import logging
from datetime import datetime

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agent.graph import build_research_graph, create_initial_state
from evaluation.eval_data import PERSONAS
from evaluation.evaluator import evaluate_persona, EvalMetrics
from config.settings import settings


def run_evaluation(personas=None, max_iterations: int = 3):
    """Run the agent on each persona and compute evaluation metrics.

    Args:
        personas: List of persona dicts to evaluate. Defaults to all 3.
        max_iterations: Max search iterations per persona (lower for eval speed).
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    logger = logging.getLogger(__name__)

    if personas is None:
        personas = PERSONAS

    graph = build_research_graph()
    all_metrics: list[EvalMetrics] = []

    for persona in personas:
        logger.info(f"\n{'='*60}")
        logger.info(f"Evaluating: {persona['name']} ({persona['context']})")
        logger.info(f"{'='*60}")

        initial_state = create_initial_state(
            target_name=persona["name"],
            target_context=persona["context"],
            max_iterations=max_iterations,
        )

        # Run the agent
        final_state = None
        try:
            for step in graph.stream(initial_state):
                node_name = list(step.keys())[0]
                node_output = step[node_name]
                for log in node_output.get("execution_log", []):
                    logger.info(f"  {log}")
                final_state = node_output
        except Exception as e:
            logger.error(f"Agent failed for {persona['name']}: {e}")
            continue

        if not final_state:
            logger.error(f"No output for {persona['name']}")
            continue

        # Extract facts and entities from cumulative state
        # Note: stream returns the last node's output, not cumulative state
        # For proper eval, we use graph.invoke() instead
        try:
            result = graph.invoke(initial_state)
            extracted_facts = result.get("facts", [])
            extracted_entities = result.get("entities", [])
        except Exception as e:
            logger.error(f"Re-invocation failed for {persona['name']}: {e}")
            continue

        # Compute metrics
        metrics = evaluate_persona(persona, extracted_facts, extracted_entities)
        all_metrics.append(metrics)
        logger.info(f"\n{metrics.summary()}")

    # --- Aggregate report ---
    print(f"\n{'='*60}")
    print(f"  EVALUATION REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    for m in all_metrics:
        print(m.summary())

    if all_metrics:
        avg_recall = sum(m.recall for m in all_metrics) / len(all_metrics)
        avg_coverage = sum(m.category_coverage for m in all_metrics) / len(all_metrics)
        avg_depth = sum(m.depth_score for m in all_metrics) / len(all_metrics)
        print(f"--- AVERAGES ---")
        print(f"  Average Recall:            {avg_recall:.1%}")
        print(f"  Average Category Coverage: {avg_coverage:.1%}")
        print(f"  Average Depth Score:       {avg_depth:.1%}\n")

    # Save report
    os.makedirs(settings.reports_dir, exist_ok=True)
    report_path = os.path.join(settings.reports_dir, "evaluation_report.json")
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "personas": [
            {
                "name": m.persona_name,
                "recall": m.recall,
                "category_coverage": m.category_coverage,
                "depth_score": m.depth_score,
                "total_extracted_facts": m.total_extracted_facts,
                "total_extracted_entities": m.total_extracted_entities,
                "matched": m.matched_facts,
                "missed": m.missed_facts,
            }
            for m in all_metrics
        ],
    }
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"Report saved to: {report_path}")
    return all_metrics


if __name__ == "__main__":
    # Allow running a single persona by index: python run_eval.py 1
    if len(sys.argv) > 1:
        idx = int(sys.argv[1]) - 1
        run_evaluation(personas=[PERSONAS[idx]], max_iterations=3)
    else:
        run_evaluation(max_iterations=3)
