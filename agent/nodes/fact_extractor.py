"""Node 3: Fact Extractor — extracts structured facts from search results.

Uses Groq (Llama 3.3 70B) as primary, with Gemini fallback on rate limits.
"""

import json
import logging
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import settings
from agent.llm_retry import invoke_with_retry
from agent.state import (
    AgentState,
    ExtractedFact,
    Entity,
    EntityType,
    FactCategory,
)
from agent.prompts.templates import FACT_EXTRACTOR_PROMPT

logger = logging.getLogger(__name__)

ENTITY_TYPE_MAP = {
    "person": EntityType.PERSON,
    "organization": EntityType.ORGANIZATION,
    "event": EntityType.EVENT,
    "filing": EntityType.FILING,
    "location": EntityType.LOCATION,
}

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
        ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.1),
        "groq",
    )
    if settings.google_api_key:
        yield (
            ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.1,
            ),
            "gemini-fallback",
        )


def fact_extractor(state: AgentState) -> dict:
    """Extract structured facts and entities from search results.

    Processes the most recent search results (up to 10) and outputs
    subject-predicate-object triples with confidence scores.
    Falls back to Gemini if Groq hits rate limits.
    """
    all_results = state.get("search_results", [])
    if not all_results:
        return {
            "execution_log": [f"[{datetime.now().isoformat()}] FactExtractor: No search results to process"],
        }

    # Take the most recent results (up to 10)
    results_to_process = all_results[-10:]

    # Format search results for the prompt
    results_text = ""
    for i, r in enumerate(results_to_process, 1):
        results_text += f"\n--- Result {i} (query: {r.query}) ---\n"
        results_text += f"Title: {r.title}\n"
        results_text += f"URL: {r.url}\n"
        results_text += f"Content: {r.content[:2000]}\n"

    prompt = FACT_EXTRACTOR_PROMPT.format(
        target_name=state["target_name"],
        target_context=state.get("target_context", ""),
        search_results=results_text,
    )

    # Try each LLM candidate until one succeeds
    last_error = None
    for llm, label in _get_llm_candidates():
        try:
            response = invoke_with_retry(llm, prompt, label=f"FactExtractor/{label}")
            content = response.content

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())

            # Parse facts
            new_facts = []
            for f in data.get("facts", [])[:settings.max_facts_per_extraction]:
                category = CATEGORY_MAP.get(f.get("category", "professional"), FactCategory.PROFESSIONAL)
                new_facts.append(ExtractedFact(
                    subject=f["subject"],
                    predicate=f["predicate"],
                    object=f["object"],
                    confidence=min(max(float(f.get("confidence", 0.5)), 0.0), 1.0),
                    category=category,
                    source_url=f.get("source_url", ""),
                ))

            # Parse new entities
            new_entities = []
            existing_names = {e.name.lower() for e in state.get("entities", [])}
            for e in data.get("new_entities", []):
                name = e.get("name", "").strip()
                if not name or name.lower() in existing_names:
                    continue
                existing_names.add(name.lower())
                entity_type = ENTITY_TYPE_MAP.get(e.get("entity_type", "organization"), EntityType.ORGANIZATION)
                new_entities.append(Entity(
                    name=name,
                    entity_type=entity_type,
                    description=e.get("description", ""),
                ))

            log_msg = (
                f"[{datetime.now().isoformat()}] FactExtractor ({label}): "
                f"Extracted {len(new_facts)} facts, {len(new_entities)} new entities"
            )
            logger.info(log_msg)

            return {
                "facts": new_facts,
                "entities": new_entities,
                "execution_log": [log_msg],
            }

        except Exception as e:
            last_error = e
            logger.warning(f"FactExtractor ({label}) failed: {e}")
            continue

    # All LLMs failed
    return {
        "execution_log": [f"[{datetime.now().isoformat()}] FactExtractor: ALL MODELS FAILED — {last_error}"],
    }
