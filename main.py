"""CLI entry point for the research agent."""

import os
import sys
import json
import logging
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from agent.graph import build_research_graph, create_initial_state
from config.settings import settings


def setup_logging():
    """Configure logging for CLI execution."""
    os.makedirs(settings.logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(settings.logs_dir, f"run_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file),
        ],
    )
    return log_file


def main():
    """Run the research agent from the command line."""
    log_file = setup_logging()
    logger = logging.getLogger(__name__)

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py '<target_name>' ['<target_context>'] [max_iterations]")
        print("Example: python main.py 'Timothy Overturf' 'CEO of Sisu Capital' 5")
        sys.exit(1)

    target_name = sys.argv[1]
    target_context = sys.argv[2] if len(sys.argv) > 2 else ""
    max_iterations = int(sys.argv[3]) if len(sys.argv) > 3 else settings.max_search_iterations

    # Validate API keys
    missing_keys = []
    if not settings.groq_api_key:
        missing_keys.append("GROQ_API_KEY")
    if not settings.google_api_key:
        missing_keys.append("GOOGLE_API_KEY")
    if not settings.tavily_api_key:
        missing_keys.append("TAVILY_API_KEY")
    if missing_keys:
        print(f"ERROR: Missing API keys: {', '.join(missing_keys)}")
        print("Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)

    logger.info(f"Starting investigation: {target_name} ({target_context})")
    logger.info(f"Max iterations: {max_iterations}")
    logger.info(f"Log file: {log_file}")

    # Build and run the graph
    graph = build_research_graph()
    initial_state = create_initial_state(target_name, target_context, max_iterations)

    print(f"\n{'='*60}")
    print(f"  RESEARCH AGENT — Due Diligence Investigation")
    print(f"  Target: {target_name}")
    print(f"  Context: {target_context}")
    print(f"  Max iterations: {max_iterations}")
    print(f"{'='*60}\n")

    # Stream execution for live progress
    final_state = None
    for step in graph.stream(initial_state):
        node_name = list(step.keys())[0]
        node_output = step[node_name]

        # Print execution logs
        for log in node_output.get("execution_log", []):
            print(f"  {log}")

        final_state = node_output

    if not final_state:
        logger.error("Agent produced no output")
        sys.exit(1)

    # Print summary
    print(f"\n{'='*60}")
    print(f"  INVESTIGATION COMPLETE")
    print(f"{'='*60}")

    # Save execution log
    os.makedirs(settings.logs_dir, exist_ok=True)
    safe_name = target_name.replace(" ", "_").replace(",", "")[:50]
    log_json_path = os.path.join(settings.logs_dir, f"{safe_name}_execution.json")

    # We need to get the full final state from the graph
    # The stream gives us the last node's output, but we need cumulative state
    # Re-invoke to get full state (or we collect from stream)
    print(f"\n  Log file: {log_file}")
    print(f"  Check outputs/ directory for graph and report files.\n")


if __name__ == "__main__":
    main()
