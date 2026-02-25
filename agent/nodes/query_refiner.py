"""Node 5: Query Refiner — decides whether to continue searching and generates refined queries.

Uses Groq/Llama as primary, with Gemini fallback on rate limits.
This is the control flow hub of the search loop — it examines what's been
found so far and decides whether the investigation should go deeper.
"""

import json
import logging
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from config.settings import settings
from agent.state import AgentState, SearchQuery, FactCategory
from agent.prompts.templates import QUERY_REFINER_PROMPT

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
        ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2),
        "groq",
    )
    if settings.google_api_key:
        yield (
            ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.2,
            ),
            "gemini-fallback",
        )


def query_refiner(state: AgentState) -> dict:
    """Decide whether to continue the search loop or finalize.

    Examines uninvestigated entities, low-confidence facts, and risk flags
    to determine if further searching would add value.
    Falls back to Gemini if Groq hits rate limits.
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", settings.max_search_iterations)

    # If we've hit max iterations, stop
    if iteration >= max_iterations:
        log_msg = f"[{datetime.now().isoformat()}] QueryRefiner: Max iterations ({max_iterations}) reached — stopping"
        return {
            "should_continue": False,
            "iteration": iteration,
            "execution_log": [log_msg],
        }

    # Find uninvestigated entities
    uninvestigated = [e for e in state.get("entities", []) if not e.investigated]
    uninvestigated_text = "\n".join(
        f"- {e.name} ({e.entity_type.value}): {e.description}"
        for e in uninvestigated[:10]
    ) or "None"

    # Find low-confidence facts
    low_conf_facts = [f for f in state.get("facts", []) if f.confidence < 0.5]
    low_conf_text = "\n".join(
        f"- {f.subject} {f.predicate} {f.object} (confidence: {f.confidence})"
        for f in low_conf_facts[:10]
    ) or "None"

    # Risk flags
    risk_text = "\n".join(
        f"- [{r.severity.value}/5] {r.description}"
        for r in state.get("risk_flags", [])
    ) or "None"

    prompt = QUERY_REFINER_PROMPT.format(
        target_name=state["target_name"],
        target_context=state.get("target_context", ""),
        iteration=iteration + 1,
        max_iterations=max_iterations,
        uninvestigated_entities=uninvestigated_text,
        risk_flags=risk_text,
        low_confidence_facts=low_conf_text,
        completed_queries="\n".join(state.get("completed_queries", [])) or "none",
    )

    # Try each LLM candidate until one succeeds
    last_error = None
    for llm, label in _get_llm_candidates():
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())

            should_continue = data.get("should_continue", False)
            new_queries = []

            if should_continue:
                for q in data.get("new_queries", []):
                    category = CATEGORY_MAP.get(q.get("category", "professional"), FactCategory.PROFESSIONAL)
                    new_queries.append(SearchQuery(
                        query=q["query"],
                        category=category,
                        rationale=q.get("rationale", ""),
                    ))

            log_msg = (
                f"[{datetime.now().isoformat()}] QueryRefiner ({label}): "
                f"{'CONTINUE' if should_continue else 'STOP'} — "
                f"{data.get('reasoning', 'no reasoning')} "
                f"({len(new_queries)} new queries)"
            )
            logger.info(log_msg)

            return {
                "should_continue": should_continue,
                "search_queries": new_queries,
                "iteration": iteration + 1,
                "execution_log": [log_msg],
            }

        except Exception as e:
            last_error = e
            logger.warning(f"QueryRefiner ({label}) failed: {e}")
            continue

    # All LLMs failed — stop the loop to prevent infinite retries
    return {
        "should_continue": False,
        "iteration": iteration + 1,
        "execution_log": [f"[{datetime.now().isoformat()}] QueryRefiner: ALL MODELS FAILED (stopping) — {last_error}"],
    }
