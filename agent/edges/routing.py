"""Conditional edge functions for LangGraph routing decisions."""

from agent.state import AgentState


def should_continue_search(state: AgentState) -> str:
    """Decide whether to loop back to search or proceed to graph building.

    Returns:
        "search_executor" — if more searching is needed
        "graph_builder"   — if investigation is complete
    """
    if state.get("should_continue", False) and state.get("iteration", 0) < state.get("max_iterations", 5):
        return "search_executor"
    return "graph_builder"
