"""LangGraph StateGraph assembly — wires all nodes and edges together.

This is the heart of the agent: a directed graph that orchestrates
the research pipeline with a conditional search loop.

Flow:
  START → query_planner → search_executor → fact_extractor
       → risk_analyzer → query_refiner → [CONDITIONAL]
           ├─ should_continue=True  → search_executor (loop)
           └─ should_continue=False → graph_builder → report_generator → END
"""

import logging

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes.query_planner import query_planner
from agent.nodes.search_executor import search_executor
from agent.nodes.fact_extractor import fact_extractor
from agent.nodes.risk_analyzer import risk_analyzer
from agent.nodes.query_refiner import query_refiner
from agent.nodes.graph_builder import graph_builder
from agent.nodes.report_generator import report_generator
from agent.edges.routing import should_continue_search

logger = logging.getLogger(__name__)


def build_research_graph() -> StateGraph:
    """Build and compile the research agent graph.

    Returns a compiled LangGraph that can be invoked with an initial state.
    """
    workflow = StateGraph(AgentState)

    # --- Add nodes ---
    workflow.add_node("query_planner", query_planner)
    workflow.add_node("search_executor", search_executor)
    workflow.add_node("fact_extractor", fact_extractor)
    workflow.add_node("risk_analyzer", risk_analyzer)
    workflow.add_node("query_refiner", query_refiner)
    workflow.add_node("graph_builder", graph_builder)
    workflow.add_node("report_generator", report_generator)

    # --- Add edges ---
    # Linear flow: plan → search → extract → analyze → refine
    workflow.set_entry_point("query_planner")
    workflow.add_edge("query_planner", "search_executor")
    workflow.add_edge("search_executor", "fact_extractor")
    workflow.add_edge("fact_extractor", "risk_analyzer")
    workflow.add_edge("risk_analyzer", "query_refiner")

    # Conditional: refine → search (loop) OR refine → graph_builder (finalize)
    workflow.add_conditional_edges(
        "query_refiner",
        should_continue_search,
        {
            "search_executor": "search_executor",
            "graph_builder": "graph_builder",
        },
    )

    # Finalization: graph → report → END
    workflow.add_edge("graph_builder", "report_generator")
    workflow.add_edge("report_generator", END)

    return workflow.compile()


def create_initial_state(target_name: str, target_context: str = "", max_iterations: int = 5) -> AgentState:
    """Create the initial state for a research investigation.

    Args:
        target_name: The person to investigate (e.g., "Timothy Overturf")
        target_context: Additional context (e.g., "CEO of Sisu Capital")
        max_iterations: Maximum search loop iterations (default: 5)
    """
    return {
        "target_name": target_name,
        "target_context": target_context,
        "search_queries": [],
        "search_results": [],
        "completed_queries": [],
        "entities": [],
        "facts": [],
        "risk_flags": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "should_continue": False,
        "graph_html": "",
        "report": "",
        "execution_log": [],
    }
