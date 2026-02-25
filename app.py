"""Streamlit UI for the Research Agent — live demo interface."""

import os
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent.graph import build_research_graph, create_initial_state
from config.settings import settings


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
    - **Model 2**: Gemini 2.5 Flash — risk analysis
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

run_btn = st.button("🚀 Start Investigation", type="primary", use_container_width=True)

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
    progress_container = st.container()
    progress_bar = st.progress(0, text="Starting investigation...")

    # Placeholders for results
    log_expander = st.expander("📋 Execution Log", expanded=True)
    logs: list[str] = []

    # Stream execution
    final_state = None
    node_count = 0
    total_expected_nodes = 7  # Rough estimate for progress bar

    try:
        for step in graph.stream(initial_state):
            node_name = list(step.keys())[0]
            node_output = step[node_name]
            node_count += 1

            # Update progress
            progress = min(node_count / (total_expected_nodes * max_iter), 0.95)
            progress_bar.progress(progress, text=f"Running: {node_name}...")

            # Collect logs
            for log in node_output.get("execution_log", []):
                logs.append(log)
                with log_expander:
                    st.text(log)

            final_state = node_output

        progress_bar.progress(1.0, text="✅ Investigation complete!")

    except Exception as e:
        st.error(f"Agent error: {e}")
        st.stop()

    # --- Results: invoke for full state ---
    st.divider()
    st.header("📊 Results")

    try:
        result = graph.invoke(initial_state)
    except Exception:
        result = {}  # Fallback if re-invoke fails

    # Tabs for different result views
    tab_report, tab_graph, tab_facts, tab_risks, tab_entities = st.tabs([
        "📝 Report", "🕸️ Identity Graph", "📋 Facts", "⚠️ Risks", "👥 Entities"
    ])

    with tab_report:
        report = result.get("report", "No report generated.")
        st.markdown(report)

    with tab_graph:
        graph_html_path = result.get("graph_html", "")
        if graph_html_path and os.path.exists(graph_html_path):
            with open(graph_html_path, "r") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        else:
            st.info("No identity graph generated.")

    with tab_facts:
        facts = result.get("facts", [])
        if facts:
            st.metric("Total Facts", len(facts))
            for f in facts:
                confidence_color = "🟢" if f.confidence >= 0.7 else "🟡" if f.confidence >= 0.4 else "🔴"
                st.markdown(
                    f"{confidence_color} **{f.subject}** {f.predicate} **{f.object}** "
                    f"— _{f.category.value}_ ({f.confidence:.0%})"
                )
        else:
            st.info("No facts extracted.")

    with tab_risks:
        risks = result.get("risk_flags", [])
        if risks:
            st.metric("Total Risk Flags", len(risks))
            sorted_risks = sorted(risks, key=lambda r: r.severity.value, reverse=True)
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
        entities = result.get("entities", [])
        if entities:
            st.metric("Total Entities", len(entities))
            for e in entities:
                type_icon = {
                    "person": "👤", "organization": "🏢",
                    "event": "📅", "filing": "📄", "location": "📍"
                }.get(e.entity_type.value, "❓")
                st.markdown(f"{type_icon} **{e.name}** ({e.entity_type.value}) — {e.description}")
        else:
            st.info("No entities discovered.")
