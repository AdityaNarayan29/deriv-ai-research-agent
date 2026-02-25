"""Node 1: Query Planner — generates initial search queries.

Uses Groq (Llama 3.3 70B) as primary, with Gemini fallback on rate limits.
"""

import json
import logging
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
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


def _get_llm_candidates():
    """Yield (llm, label) pairs — primary Groq, then Gemini fallback."""
    yield (
        ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.3),
        "groq",
    )
    if settings.google_api_key:
        yield (
            ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.3,
            ),
            "gemini-fallback",
        )


def query_planner(state: AgentState) -> dict:
    """Generate search queries for the target person.

    Uses Groq/Llama to create diverse, targeted queries covering
    biographical, professional, financial, legal, and social aspects.
    Falls back to Gemini if Groq hits rate limits.
    """
    # Build previous findings summary if we have facts
    previous_findings = ""
    if state.get("facts"):
        facts_summary = "\n".join(
            f"- {f.subject} {f.predicate} {f.object} (confidence: {f.confidence})"
            for f in state["facts"][:20]
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

    # Try each LLM candidate until one succeeds
    last_error = None
    for llm, label in _get_llm_candidates():
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content

            # Parse JSON from response
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

            log_msg = (
                f"[{datetime.now().isoformat()}] QueryPlanner ({label}): "
                f"Generated {len(queries)} queries (iteration {state.get('iteration', 0)})"
            )
            logger.info(log_msg)

            return {
                "search_queries": queries,
                "execution_log": [log_msg],
            }

        except Exception as e:
            last_error = e
            logger.warning(f"QueryPlanner ({label}) failed: {e}")
            continue

    # All LLMs failed — generate basic hardcoded queries as last resort
    logger.error(f"QueryPlanner: all models failed, using hardcoded fallback: {last_error}")
    fallback_queries = [
        SearchQuery(query=f"{state['target_name']} {state.get('target_context', '')}", category=FactCategory.PROFESSIONAL),
        SearchQuery(query=f"{state['target_name']} background biography", category=FactCategory.BIOGRAPHICAL),
        SearchQuery(query=f"{state['target_name']} SEC filings regulatory", category=FactCategory.LEGAL),
    ]
    return {
        "search_queries": fallback_queries,
        "execution_log": [f"[{datetime.now().isoformat()}] QueryPlanner: ALL MODELS FAILED — using hardcoded fallback"],
    }
