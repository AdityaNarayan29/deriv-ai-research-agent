"""Streamlit UI for the Research Agent — live demo interface."""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent.graph import build_research_graph, create_initial_state
from agent.state import AgentState, ExtractedFact, Entity, RiskFlag, FactCategory, EntityType, RiskCategory, RiskSeverity
from config.settings import settings
from demo_data import (
    DEMO_FACTS, DEMO_ENTITIES, DEMO_RISK_FLAGS,
    DEMO_REPORT, DEMO_EXECUTION_LOG,
)


# --- Page config ---
st.set_page_config(
    page_title="AI Research Agent — Due Diligence",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI Research Agent")
st.caption("Autonomous due diligence investigation powered by LangGraph + Groq + Gemini")

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")

    max_iter = st.slider("Max search iterations", 1, 10, settings.max_search_iterations)

    st.divider()
    st.header("📊 Tech Stack")
    st.markdown("""
    - **Agent**: LangGraph
    - **Model 1**: Groq (Llama 3.3 70B) — extraction
    - **Model 2**: Gemini 2.0 Flash — risk analysis
    - **Search**: Tavily API
    - **Graph**: NetworkX + pyvis
    - **Tracing**: LangSmith
    """)

    # API key status
    st.divider()
    st.header("🔑 API Key Status")
    st.markdown(f"- Groq: {'✅' if settings.groq_api_key else '❌'}")
    st.markdown(f"- Gemini: {'✅' if settings.google_api_key else '❌'}")
    st.markdown(f"- Tavily: {'✅' if settings.tavily_api_key else '❌'}")
    st.markdown(f"- LangSmith: {'✅' if settings.langchain_api_key else '⚠️ (optional)'}")


# --- Main input ---
col1, col2 = st.columns([2, 1])
with col1:
    target_name = st.text_input("Target Name", value="Timothy Overturf", placeholder="Enter person's name")
with col2:
    target_context = st.text_input("Context", value="CEO of Sisu Capital", placeholder="e.g., CEO of Company X")

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    run_btn = st.button("🚀 Start Investigation", type="primary", use_container_width=True)
with col_btn2:
    demo_btn = st.button("🎯 Demo", use_container_width=True)

# --- Demo Mode ---
if demo_btn:
    st.divider()
    st.header("📊 Results  `DEMO`")

    # Convert demo dicts → Pydantic models
    facts = [ExtractedFact(**{**f, "category": FactCategory(f["category"])}) for f in DEMO_FACTS]
    entities = [Entity(**{**e, "entity_type": EntityType(e["entity_type"])}) for e in DEMO_ENTITIES]
    risk_flags = [RiskFlag(**{**r, "severity": RiskSeverity(r["severity"]), "category": RiskCategory(r["category"])}) for r in DEMO_RISK_FLAGS]

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Facts Extracted", len(facts))
    col_m2.metric("Entities Discovered", len(entities))
    col_m3.metric("Risk Flags", len(risk_flags))
    col_m4.metric("Search Iterations", 2)

    tab_report, tab_graph, tab_facts, tab_risks, tab_entities, tab_log = st.tabs([
        "📝 Report", "🕸️ Identity Graph", "📋 Facts", "⚠️ Risks", "👥 Entities", "📋 Log"
    ])

    with tab_report:
        st.markdown(DEMO_REPORT)

    with tab_graph:
        st.info("Identity graph is generated only during live investigations. Use the Next.js UI at localhost:3000 for the interactive React Flow graph.")

    with tab_facts:
        for f in facts:
            confidence_color = "🟢" if f.confidence >= 0.7 else "🟡" if f.confidence >= 0.4 else "🔴"
            st.markdown(
                f"{confidence_color} **{f.subject}** {f.predicate} **{f.object}** "
                f"— _{f.category.value}_ ({f.confidence:.0%})"
            )

    with tab_risks:
        sorted_risks = sorted(risk_flags, key=lambda r: r.severity.value, reverse=True)
        for r in sorted_risks:
            severity_icon = {1: "ℹ️", 2: "⚠️", 3: "🟠", 4: "🔴", 5: "🚨"}.get(r.severity.value, "⚠️")
            st.markdown(
                f"{severity_icon} **[{r.severity.value}/5 — {r.category.value}]** {r.description}"
            )
            if r.recommendation:
                st.caption(f"→ {r.recommendation}")

    with tab_entities:
        for e in entities:
            type_icon = {
                "person": "👤", "organization": "🏢",
                "event": "📅", "filing": "📄", "location": "📍"
            }.get(e.entity_type.value, "❓")
            st.markdown(f"{type_icon} **{e.name}** ({e.entity_type.value}) — {e.description}")

    with tab_log:
        for line in DEMO_EXECUTION_LOG:
            st.text(line)

    st.stop()

# --- Execution ---
if run_btn:
    if not target_name:
        st.error("Please enter a target name.")
        st.stop()

    # Validate keys
    missing = []
    if not settings.groq_api_key:
        missing.append("GROQ_API_KEY")
    if not settings.google_api_key:
        missing.append("GOOGLE_API_KEY")
    if not settings.tavily_api_key:
        missing.append("TAVILY_API_KEY")
    if missing:
        st.error(f"Missing API keys: {', '.join(missing)}. Add them to your `.env` file.")
        st.stop()

    # Build graph
    graph = build_research_graph()
    initial_state = create_initial_state(target_name, target_context, max_iter)

    # Progress display
    progress_bar = st.progress(0, text="Starting investigation...")

    # Execution log
    log_expander = st.expander("📋 Execution Log", expanded=True)
    logs: list[str] = []

    # ------------------------------------------------------------------
    # Stream execution and accumulate the full state from partial outputs.
    # Each node yields its slice of the state; we merge them together
    # exactly like LangGraph's internal reducers do, so we end up with
    # the same final state that `graph.invoke()` would return — but
    # without running the pipeline twice.
    # ------------------------------------------------------------------
    accumulated: dict = {}
    # List-type state keys that should be extended (not overwritten)
    _LIST_KEYS = {
        "search_queries", "search_results", "completed_queries",
        "entities", "facts", "risk_flags", "execution_log",
    }
    node_count = 0
    total_expected_nodes = 7  # rough estimate for progress bar

    try:
        for step in graph.stream(initial_state):
            node_name = list(step.keys())[0]
            node_output = step[node_name]
            node_count += 1

            # Update progress
            progress = min(node_count / (total_expected_nodes * max_iter), 0.95)
            progress_bar.progress(progress, text=f"Running: {node_name}...")

            # Merge this node's output into accumulated state
            for key, value in node_output.items():
                if key in _LIST_KEYS and isinstance(value, list):
                    # Extend lists (mimics the _merge_lists / _merge_strings reducers)
                    existing = accumulated.get(key, [])
                    # Deduplicate by id if items have one
                    existing_ids = set()
                    for item in existing:
                        item_id = getattr(item, "id", None)
                        if item_id is None and isinstance(item, dict):
                            item_id = item.get("id")
                        if item_id:
                            existing_ids.add(item_id)

                    for item in value:
                        item_id = getattr(item, "id", None)
                        if item_id is None and isinstance(item, dict):
                            item_id = item.get("id")
                        if item_id and item_id in existing_ids:
                            continue
                        # For plain strings (execution_log, completed_queries), dedup by value
                        if isinstance(item, str) and item in existing:
                            continue
                        existing.append(item)

                    accumulated[key] = existing
                else:
                    # Scalar values: overwrite (latest wins)
                    accumulated[key] = value

            # Show new log lines live
            for log_line in node_output.get("execution_log", []):
                if log_line not in logs:
                    logs.append(log_line)
                    with log_expander:
                        st.text(log_line)

        progress_bar.progress(1.0, text="✅ Investigation complete!")

    except Exception as e:
        progress_bar.progress(1.0, text="⚠️ Investigation finished with errors.")
        st.warning(f"Agent encountered an error: {e}")

    # Merge initial state scalars that nodes may not have re-emitted
    for key in ("target_name", "target_context"):
        if key not in accumulated:
            accumulated[key] = initial_state[key]

    # --- Results ---
    st.divider()
    st.header("📊 Results")

    # Summary metrics row
    facts = accumulated.get("facts", [])
    entities = accumulated.get("entities", [])
    risk_flags = accumulated.get("risk_flags", [])
    iterations = accumulated.get("iteration", 0)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Facts Extracted", len(facts))
    col_m2.metric("Entities Discovered", len(entities))
    col_m3.metric("Risk Flags", len(risk_flags))
    col_m4.metric("Search Iterations", iterations)

    # Tabs for different result views
    tab_report, tab_graph, tab_facts, tab_risks, tab_entities = st.tabs([
        "📝 Report", "🕸️ Identity Graph", "📋 Facts", "⚠️ Risks", "👥 Entities"
    ])

    with tab_report:
        report = accumulated.get("report", "")
        if report:
            st.markdown(report)
        else:
            st.info("No report generated. This may be due to API rate limits.")

    with tab_graph:
        graph_html_path = accumulated.get("graph_html", "")
        if graph_html_path and os.path.exists(graph_html_path):
            with open(graph_html_path, "r") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        else:
            st.info("No identity graph generated.")

    with tab_facts:
        if facts:
            for f in facts:
                confidence_color = "🟢" if f.confidence >= 0.7 else "🟡" if f.confidence >= 0.4 else "🔴"
                st.markdown(
                    f"{confidence_color} **{f.subject}** {f.predicate} **{f.object}** "
                    f"— _{f.category.value}_ ({f.confidence:.0%})"
                )
        else:
            st.info("No facts extracted.")

    with tab_risks:
        if risk_flags:
            sorted_risks = sorted(risk_flags, key=lambda r: r.severity.value, reverse=True)
            for r in sorted_risks:
                severity_icon = {1: "ℹ️", 2: "⚠️", 3: "🟠", 4: "🔴", 5: "🚨"}.get(r.severity.value, "⚠️")
                st.markdown(
                    f"{severity_icon} **[{r.severity.value}/5 — {r.category.value}]** {r.description}"
                )
                if r.recommendation:
                    st.caption(f"→ {r.recommendation}")
        else:
            st.info("No risk flags identified.")

    with tab_entities:
        if entities:
            for e in entities:
                type_icon = {
                    "person": "👤", "organization": "🏢",
                    "event": "📅", "filing": "📄", "location": "📍"
                }.get(e.entity_type.value, "❓")
                st.markdown(f"{type_icon} **{e.name}** ({e.entity_type.value}) — {e.description}")
        else:
            st.info("No entities discovered.")
