"""LangGraph StateGraph assembly — wires all nodes and edges together.

This is the heart of the agent: a directed graph that orchestrates
the research pipeline with a conditional search loop.

Flow:
  START → query_planner → search_executor → fact_extractor
       → risk_analyzer → query_refiner → [CONDITIONAL]
           ├─ should_continue=True  → search_executor (loop)
           └─ should_continue=False → graph_builder → report_generator → END
"""

import os
import logging

from langgraph.graph import StateGraph, END

from config.settings import settings
from agent.state import AgentState, Entity, EntityType


def _configure_langsmith():
    """Set LangSmith environment variables so LangChain auto-traces all LLM calls."""
    if settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project


_configure_langsmith()
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
    # Seed the target as the first entity so search_executor can mark it
    # investigated after iteration 1. Hardcoded as PERSON — due diligence
    # targets are almost always individuals. If the target is an org,
    # fact_extractor will discover the correct type and the graph_builder
    # fuzzy match handles both.
    target_entity = Entity(
        name=target_name,
        entity_type=EntityType.PERSON,
        description=target_context,
        investigated=False,
    )

    return {
        "target_name": target_name,
        "target_context": target_context,
        "search_queries": [],
        "search_results": [],
        "completed_queries": [],
        "entities": [target_entity],
        "facts": [],
        "risk_flags": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "should_continue": False,
        "graph_html": "",
        "report": "",
        "execution_log": [],
    }
