"""Node 7: Report Generator — generates structured risk assessment report.

Primary: Google Gemini for analytical report writing.
Fallback: Groq/Llama if Gemini is rate-limited.
"""

import os
import logging
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from config.settings import settings
from agent.llm_retry import invoke_with_retry
from agent.state import AgentState
from agent.prompts.templates import REPORT_GENERATOR_PROMPT

logger = logging.getLogger(__name__)


def _get_llm_candidates():
    """Yield (llm, name) pairs to try in order: Gemini first, then Groq."""
    yield (
        ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.3,
        ),
        "gemini",
    )
    yield (
        ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0.3,
        ),
        "groq-fallback",
    )


def _format_network_analysis(graph_analytics: dict) -> str:
    """Build a human-readable NETWORK ANALYSIS block for the report prompt.

    Returns a readable text block if meaningful analytics exist, or a
    short note if the graph is too small (< 5 nodes or < 5 edges).
    """
    if not graph_analytics:
        return "NETWORK ANALYSIS:\n- No network analytics available."

    total_nodes = graph_analytics.get("total_nodes", 0)
    total_edges = graph_analytics.get("total_edges", 0)

    if total_nodes < 5 or total_edges < 5:
        return (
            f"NETWORK ANALYSIS:\n"
            f"- Graph too small for meaningful network analysis "
            f"({total_nodes} entities, {total_edges} relationships). "
            f"Relying on fact-level evidence only."
        )

    lines = [
        "NETWORK ANALYSIS:",
        f"- Graph size: {total_nodes} entities, {total_edges} relationships",
    ]

    betweenness = graph_analytics.get("top_entities_by_betweenness", [])
    if betweenness:
        lines.append("- Most central entities (by betweenness centrality):")
        for i, entry in enumerate(betweenness[:5], 1):
            lines.append(f"  {i}. {entry['name']} ({entry['score']:.3f})")

    degree = graph_analytics.get("top_entities_by_degree", [])
    if degree:
        lines.append("- Most connected entities (by degree centrality):")
        for i, entry in enumerate(degree[:5], 1):
            lines.append(f"  {i}. {entry['name']} ({entry['score']:.3f})")

    num_communities = graph_analytics.get("num_communities", 0)
    largest = graph_analytics.get("largest_community_size", 0)
    components = graph_analytics.get("num_connected_components", 0)

    if num_communities:
        lines.append(f"- Communities detected: {num_communities} distinct groups")
    if largest:
        lines.append(f"- Largest community: {largest} entities")
    if components:
        lines.append(f"- Connected components: {components}")

    return "\n".join(lines)


def report_generator(state: AgentState) -> dict:
    """Generate the final due diligence risk assessment report."""
    facts = state.get("facts", [])
    entities = state.get("entities", [])
    risk_flags = state.get("risk_flags", [])

    # Format facts
    facts_text = "\n".join(
        f"- [{f.id}] {f.subject} {f.predicate} {f.object} "
        f"(confidence: {f.confidence:.0%}, source: {f.source_url})"
        for f in facts
    ) or "No facts extracted"

    # Format entities
    entities_text = "\n".join(
        f"- {e.name} ({e.entity_type.value}): {e.description}"
        for e in entities
    ) or "No entities discovered"

    # Format risk flags (sorted by severity)
    sorted_risks = sorted(risk_flags, key=lambda r: r.severity.value, reverse=True)
    risks_text = "\n".join(
        f"- [{r.severity.value}/5 {r.category.value}] {r.description}\n"
        f"  Evidence: {', '.join(r.evidence_fact_ids)}\n"
        f"  Recommendation: {r.recommendation}"
        for r in sorted_risks
    ) or "No risk flags identified"

    # Format network analytics
    network_analysis_text = _format_network_analysis(state.get("graph_analytics", {}))

    prompt = REPORT_GENERATOR_PROMPT.format(
        target_name=state["target_name"],
        target_context=state.get("target_context", ""),
        facts=facts_text,
        entities=entities_text,
        risk_flags=risks_text,
        network_analysis=network_analysis_text,
        iterations=state.get("iteration", 0),
        total_facts=len(facts),
        total_entities=len(entities),
        total_risks=len(risk_flags),
    )

    # Try Gemini first, fall back to Groq
    for llm, model_name in _get_llm_candidates():
        try:
            response = invoke_with_retry(llm, prompt, label=f"ReportGenerator/{model_name}")
            report = response.content

            # Save report to file
            os.makedirs(settings.reports_dir, exist_ok=True)
            safe_name = state["target_name"].replace(" ", "_").replace(",", "")[:50]
            report_path = os.path.join(settings.reports_dir, f"{safe_name}_report.md")

            with open(report_path, "w") as f:
                f.write(f"# Due Diligence Report: {state['target_name']}\n")
                f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                f.write(report)

            log_msg = (
                f"[{datetime.now().isoformat()}] ReportGenerator ({model_name}): "
                f"Generated report ({len(report)} chars) → {report_path}"
            )
            logger.info(log_msg)

            return {
                "report": report,
                "execution_log": [log_msg],
            }

        except Exception as e:
            logger.warning(f"Report generation failed with {model_name}: {e}")
            continue

    # All models failed — use fallback
    fallback = _generate_fallback_report(state)
    return {
        "report": fallback,
        "execution_log": [f"[{datetime.now().isoformat()}] ReportGenerator: ALL MODELS FAILED — using raw fallback"],
    }


def _generate_fallback_report(state: AgentState) -> str:
    """Generate a basic report without LLM if all models fail."""
    lines = [
        f"# Due Diligence Report: {state['target_name']}",
        f"*Context: {state.get('target_context', 'N/A')}*\n",
        "## Facts Discovered\n",
    ]
    for f in state.get("facts", []):
        lines.append(f"- {f.subject} {f.predicate} {f.object} (confidence: {f.confidence:.0%})")

    lines.append("\n## Risk Flags\n")
    for r in sorted(state.get("risk_flags", []), key=lambda x: x.severity.value, reverse=True):
        lines.append(f"- **[{r.severity.value}/5]** {r.description}")

    lines.append("\n## Entities\n")
    for e in state.get("entities", []):
        lines.append(f"- {e.name} ({e.entity_type.value})")

    # Network analytics (raw dump) — only if data exists
    ga = state.get("graph_analytics", {})
    if ga and ga.get("total_nodes", 0) >= 5:
        lines.append("\n## Network Analysis (raw)\n")
        lines.append(f"Graph size: {ga.get('total_nodes', 0)} entities, {ga.get('total_edges', 0)} relationships.\n")

        betweenness = ga.get("top_entities_by_betweenness", [])
        if betweenness:
            lines.append("Most central entities (betweenness):")
            for entry in betweenness[:5]:
                lines.append(f"- {entry['name']} ({entry['score']:.3f})")

        degree = ga.get("top_entities_by_degree", [])
        if degree:
            lines.append("\nMost connected entities (degree):")
            for entry in degree[:5]:
                lines.append(f"- {entry['name']} ({entry['score']:.3f})")

        lines.append(f"\nCommunities detected: {ga.get('num_communities', 0)}")
        lines.append(f"Largest community: {ga.get('largest_community_size', 0)} entities")

    return "\n".join(lines)
