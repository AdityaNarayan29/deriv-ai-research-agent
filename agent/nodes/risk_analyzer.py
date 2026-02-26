"""Node 4: Risk Analyzer — cross-references facts and flags risks.

Primary: Google Gemini for strong analytical reasoning.
Fallback: Groq/Llama if Gemini is rate-limited.
"""

import json
import logging
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from config.settings import settings
from agent.llm_retry import invoke_with_retry
from agent.state import (
    AgentState,
    RiskFlag,
    RiskCategory,
    RiskSeverity,
)
from agent.prompts.templates import RISK_ANALYZER_PROMPT

logger = logging.getLogger(__name__)

RISK_CATEGORY_MAP = {
    "regulatory": RiskCategory.REGULATORY,
    "reputational": RiskCategory.REPUTATIONAL,
    "financial": RiskCategory.FINANCIAL,
    "legal": RiskCategory.LEGAL,
    "inconsistency": RiskCategory.INCONSISTENCY,
}


def risk_analyzer(state: AgentState) -> dict:
    """Analyze extracted facts for risks, inconsistencies, and red flags."""
    facts = state.get("facts", [])
    entities = state.get("entities", [])
    existing_risks = state.get("risk_flags", [])

    if not facts:
        return {
            "execution_log": [f"[{datetime.now().isoformat()}] RiskAnalyzer: No facts to analyze"],
        }

    # Format facts for prompt
    facts_text = "\n".join(
        f"[{f.id}] {f.subject} {f.predicate} {f.object} "
        f"(confidence: {f.confidence}, category: {f.category.value})"
        for f in facts
    )

    entities_text = "\n".join(
        f"- {e.name} ({e.entity_type.value}): {e.description}"
        for e in entities
    )

    existing_risks_text = "\n".join(
        f"- [{r.severity.value}/5] {r.description} ({r.category.value})"
        for r in existing_risks
    ) or "None identified yet"

    prompt = RISK_ANALYZER_PROMPT.format(
        target_name=state["target_name"],
        target_context=state.get("target_context", ""),
        facts=facts_text,
        entities=entities_text,
        existing_risks=existing_risks_text,
    )

    # Try Gemini first, fall back to Groq
    model_used = "gemini"
    for attempt, (llm, model_name) in enumerate(_get_llm_candidates()):
        try:
            model_used = model_name
            response = invoke_with_retry(llm, prompt, label=f"RiskAnalyzer/{model_name}")
            content = response.content

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())

            # Parse risk flags
            new_risks = []
            for r in data.get("risk_flags", []):
                category = RISK_CATEGORY_MAP.get(r.get("category", "reputational"), RiskCategory.REPUTATIONAL)
                severity_val = min(max(int(r.get("severity", 1)), 1), 5)
                new_risks.append(RiskFlag(
                    description=r["description"],
                    severity=RiskSeverity(severity_val),
                    category=category,
                    evidence_fact_ids=r.get("evidence_fact_ids", []),
                    recommendation=r.get("recommendation", ""),
                ))

            adjustments = data.get("confidence_adjustments", [])
            adj_log = f", {len(adjustments)} confidence adjustments" if adjustments else ""

            log_msg = (
                f"[{datetime.now().isoformat()}] RiskAnalyzer ({model_used}): "
                f"Identified {len(new_risks)} risk flags{adj_log}"
            )
            logger.info(log_msg)

            return {
                "risk_flags": new_risks,
                "execution_log": [log_msg],
            }

        except Exception as e:
            logger.warning(f"Risk analysis failed with {model_name}: {e}")
            continue

    # All models failed
    return {
        "execution_log": [f"[{datetime.now().isoformat()}] RiskAnalyzer: ALL MODELS FAILED"],
    }


def _get_llm_candidates():
    """Yield (llm, name) pairs to try in order: Gemini first, then Groq."""
    yield (
        ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.2,
        ),
        "gemini",
    )
    yield (
        ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0.2,
        ),
        "groq-fallback",
    )
