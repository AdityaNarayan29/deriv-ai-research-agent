"""Node 1: Query Planner — generates initial search queries using Groq/Llama."""

import json
import logging
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config.settings import settings
from agent.state import AgentState, SearchQuery, FactCategory
from agent.prompts.templates import QUERY_PLANNER_PROMPT

logger = logging.getLogger(__name__)

CATEGORY_MAP = {
    "biographical": FactCategory.BIOGRAPHICAL,
    "professional": FactCategory.PROFESSIONAL,
    "financial": FactCategory.FINANCIAL,
    "legal": FactCategory.LEGAL,
    "social": FactCategory.SOCIAL,
    "regulatory": FactCategory.REGULATORY,
}


def query_planner(state: AgentState) -> dict:
    """Generate search queries for the target person.

    Uses Groq/Llama to create diverse, targeted queries covering
    biographical, professional, financial, legal, and social aspects.
    """
    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.3,
    )

    # Build previous findings summary if we have facts
    previous_findings = ""
    if state.get("facts"):
        facts_summary = "\n".join(
            f"- {f.subject} {f.predicate} {f.object} (confidence: {f.confidence})"
            for f in state["facts"][:20]  # Limit to avoid token overflow
        )
        entities_summary = "\n".join(
            f"- {e.name} ({e.entity_type.value}): {e.description}"
            for e in state.get("entities", [])[:15]
        )
        previous_findings = f"""
PREVIOUS FINDINGS (build upon these):
Facts discovered:
{facts_summary}

Entities discovered:
{entities_summary}
"""

    prompt = QUERY_PLANNER_PROMPT.format(
        target_name=state["target_name"],
        target_context=state.get("target_context", ""),
        previous_findings=previous_findings,
        num_queries=settings.max_queries_per_iteration,
        completed_queries=", ".join(state.get("completed_queries", [])) or "none yet",
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content

        # Parse JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        queries = []
        for q in data.get("queries", []):
            category = CATEGORY_MAP.get(q.get("category", "professional"), FactCategory.PROFESSIONAL)
            queries.append(SearchQuery(
                query=q["query"],
                category=category,
                rationale=q.get("rationale", ""),
            ))

        log_msg = f"[{datetime.now().isoformat()}] QueryPlanner: Generated {len(queries)} queries (iteration {state.get('iteration', 0)})"
        logger.info(log_msg)

        return {
            "search_queries": queries,
            "execution_log": [log_msg],
        }

    except Exception as e:
        logger.error(f"Query planner failed: {e}")
        # Fallback: generate basic queries
        fallback_queries = [
            SearchQuery(query=f"{state['target_name']} {state.get('target_context', '')}", category=FactCategory.PROFESSIONAL),
            SearchQuery(query=f"{state['target_name']} background", category=FactCategory.BIOGRAPHICAL),
            SearchQuery(query=f"{state['target_name']} SEC filings", category=FactCategory.LEGAL),
        ]
        return {
            "search_queries": fallback_queries,
            "execution_log": [f"[{datetime.now().isoformat()}] QueryPlanner: FALLBACK — {e}"],
        }
