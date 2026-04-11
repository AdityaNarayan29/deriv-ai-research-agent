"""Node 6: Graph Builder — builds identity graph using graph DB + pyvis.

Stores entities and relationships in a graph database (NetworkX + SQLite),
computes analytics (centrality, communities), and exports interactive HTML.
"""

import os
import logging
from datetime import datetime

import networkx as nx
from pyvis.network import Network

from config.settings import settings
from agent.state import AgentState, EntityType
from agent.graph_db import get_graph_db
from agent.graph_db.analytics import compute_investigation_analytics

logger = logging.getLogger(__name__)

# Modern color palette (vis.js color objects)
NODE_COLORS = {
    EntityType.PERSON: {"background": "#6366f1", "border": "#4f46e5", "highlight": {"background": "#818cf8", "border": "#4f46e5"}},
    EntityType.ORGANIZATION: {"background": "#f59e0b", "border": "#d97706", "highlight": {"background": "#fbbf24", "border": "#d97706"}},
    EntityType.EVENT: {"background": "#10b981", "border": "#059669", "highlight": {"background": "#34d399", "border": "#059669"}},
    EntityType.FILING: {"background": "#8b5cf6", "border": "#7c3aed", "highlight": {"background": "#a78bfa", "border": "#7c3aed"}},
    EntityType.LOCATION: {"background": "#ef4444", "border": "#dc2626", "highlight": {"background": "#f87171", "border": "#dc2626"}},
}

NODE_SHAPES = {
    EntityType.PERSON: "dot",
    EntityType.ORGANIZATION: "diamond",
    EntityType.EVENT: "triangle",
    EntityType.FILING: "square",
    EntityType.LOCATION: "star",
}

TARGET_COLOR = {
    "background": "#ef4444",
    "border": "#fbbf24",
    "highlight": {"background": "#f87171", "border": "#fbbf24"},
}


_STOP_WORDS = {"the", "of", "and", "for", "in", "a", "an", "inc", "corp",
                "llc", "ltd", "co", "plc", "sa", "ag", "gmbh", "na"}


def _normalize(name: str) -> str:
    """Strip corporate suffixes, punctuation, and stop words for comparison."""
    import re
    s = name.lower().strip()
    s = re.sub(r"[,.\-'\"()]", " ", s)
    tokens = [t for t in s.split() if t not in _STOP_WORDS and len(t) > 0]
    return " ".join(tokens)


def _is_acronym_of(short: str, long: str) -> bool:
    """Check if 'short' is an acronym of 'long' (e.g. SEC -> Securities and Exchange Commission)."""
    if len(short) < 2 or len(short) > 6:
        return False
    words = [w for w in long.split() if w.lower() not in _STOP_WORDS]
    if len(words) < 2:
        return False
    initials = "".join(w[0] for w in words).lower()
    return short.lower() == initials


def _fuzzy_match(text: str, known_names: dict[str, str]) -> str | None:
    """Find a known entity name that matches the text.

    Matching pipeline (in priority order):
    1. Exact case-insensitive match
    2. Normalized match (strip suffixes/stop words)
    3. Acronym match (SEC <-> Securities and Exchange Commission)
    4. Bidirectional substring match (min 4 chars to avoid false positives)
    """
    text_lower = text.lower().strip()

    # 1. Exact match
    if text_lower in known_names:
        return known_names[text_lower]

    text_norm = _normalize(text)

    # 2. Normalized match
    for known_lower, canonical in known_names.items():
        if _normalize(known_lower) == text_norm and text_norm:
            return canonical

    # 3. Acronym match
    for known_lower, canonical in known_names.items():
        if _is_acronym_of(text_lower, known_lower) or _is_acronym_of(known_lower, text_lower):
            return canonical

    # 4. Bidirectional substring (require min 4 chars to avoid "X" matching everything)
    if len(text_lower) >= 4:
        for known_lower, canonical in known_names.items():
            if len(known_lower) >= 4 and (known_lower in text_lower or text_lower in known_lower):
                return canonical

    return None


def graph_builder(state: AgentState) -> dict:
    """Build an identity graph, store in graph DB, compute analytics, export HTML.

    1. Populates the graph database with entities and fact-based relationships
    2. Computes centrality and community analytics
    3. Exports interactive pyvis HTML visualization
    """
    entities = state.get("entities", [])
    facts = state.get("facts", [])
    target_name = state["target_name"]

    if not entities and not facts:
        return {
            "execution_log": [f"[{datetime.now().isoformat()}] GraphBuilder: No entities or facts to graph"],
        }

    # --- Initialize graph database ---
    os.makedirs(settings.output_dir, exist_ok=True)
    safe_name = target_name.replace(" ", "_").replace(",", "")[:50]
    db_path = os.path.join(settings.output_dir, f"{safe_name}_graph.db")
    db = get_graph_db(db_path=db_path)
    db.clear()

    # Build lookup: lowercase name -> canonical display name
    known_names: dict[str, str] = {target_name.lower(): target_name}
    entity_type_map: dict[str, EntityType] = {}
    entity_desc_map: dict[str, str] = {}

    for e in entities:
        known_names[e.name.lower()] = e.name
        entity_type_map[e.name.lower()] = e.entity_type
        entity_desc_map[e.name.lower()] = e.description

    # Count facts per entity for node sizing
    entity_fact_count: dict[str, int] = {}
    for fact in facts:
        for text in (fact.subject, fact.object):
            match = _fuzzy_match(text, known_names)
            if match:
                entity_fact_count[match] = entity_fact_count.get(match, 0) + 1

    # --- Store target in graph DB + build pyvis graph ---
    G = nx.DiGraph()

    target_facts = entity_fact_count.get(target_name, 0)
    db.add_entity(
        entity_id=target_name,
        name=target_name,
        entity_type="target",
        properties={
            "context": state.get("target_context", ""),
            "fact_count": target_facts,
        },
    )
    G.add_node(
        target_name,
        title=f"<b>TARGET</b><br>{target_name}<br><i>{state.get('target_context', '')}</i><br>Referenced in {target_facts} fact(s)",
        color=TARGET_COLOR,
        size=50,
        shape="dot",
        borderWidth=3,
        font={"size": 18, "color": "#ffffff"},
        shadow={"enabled": True, "color": "rgba(239,68,68,0.4)", "size": 12},
    )

    # --- Store entities in graph DB + build pyvis nodes ---
    for entity in entities:
        if entity.name == target_name:
            continue
        fact_count = entity_fact_count.get(entity.name, 0)
        node_size = min(40, max(18, 14 + fact_count * 3))

        db.add_entity(
            entity_id=entity.name,
            name=entity.name,
            entity_type=entity.entity_type.value,
            properties={
                "description": entity.description,
                "fact_count": fact_count,
                "investigated": entity.investigated,
            },
        )

        tooltip = (
            f"<b>{entity.name}</b><br>"
            f"Type: {entity.entity_type.value.title()}<br>"
            f"{entity.description}<br>"
            f"<i>Referenced in {fact_count} fact(s)</i>"
        )

        G.add_node(
            entity.name,
            title=tooltip,
            color=NODE_COLORS.get(entity.entity_type, {"background": "#64748b", "border": "#475569"}),
            size=node_size,
            shape=NODE_SHAPES.get(entity.entity_type, "dot"),
            borderWidth=2,
            font={"size": 13, "color": "#e2e8f0"},
        )

    # --- Store relationships in graph DB + build pyvis edges ---
    edge_labels: dict[tuple[str, str], list[dict]] = {}

    for fact in facts:
        source_match = _fuzzy_match(fact.subject, known_names)
        target_match = _fuzzy_match(fact.object, known_names)

        if not source_match or not target_match:
            continue
        if source_match == target_match:
            continue

        # Store each fact as a relationship in the graph DB
        db.add_relationship(
            source_id=source_match,
            target_id=target_match,
            rel_type=fact.predicate,
            properties={
                "confidence": fact.confidence,
                "category": fact.category.value,
                "source_url": fact.source_url,
                "fact_id": fact.id,
            },
        )

        key = (source_match, target_match)
        if key not in edge_labels:
            edge_labels[key] = []
        edge_labels[key].append({
            "predicate": fact.predicate,
            "confidence": fact.confidence,
            "category": fact.category.value,
            "source_url": fact.source_url,
        })

    for (source, target), label_list in edge_labels.items():
        max_conf = max(l["confidence"] for l in label_list)
        width = max(1.5, max_conf * 4)
        edge_color = _edge_color(max_conf)

        display_label = min(label_list, key=lambda l: len(l["predicate"]))["predicate"]
        if len(display_label) > 25:
            display_label = display_label[:22] + "..."

        tooltip_lines = [f"<b>{source} → {target}</b><br><br>"]
        for i, l in enumerate(label_list, 1):
            tooltip_lines.append(
                f"{i}. <b>{l['predicate']}</b><br>"
                f"   Confidence: {l['confidence']:.0%} | {l['category'].title()}<br>"
            )

        G.add_edge(
            source,
            target,
            title="".join(tooltip_lines),
            label=display_label if len(label_list) == 1 else f"{display_label} (+{len(label_list)-1})",
            width=width,
            color={"color": edge_color, "highlight": edge_color, "hover": edge_color},
            font={"size": 10, "color": "#94a3b8", "strokeWidth": 3, "strokeColor": "#0f172a"},
        )

    # --- Compute graph analytics ---
    try:
        analytics = compute_investigation_analytics(db)
    except Exception as e:
        logger.warning(f"GraphBuilder: analytics computation failed: {e}")
        analytics = {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "degree_centrality_top5": [],
            "betweenness_centrality_top5": [],
            "num_components": 0,
            "largest_component_size": 0,
            "num_communities": 0,
            "community_sizes": [],
        }
    logger.info(
        f"GraphBuilder analytics: {analytics['node_count']} nodes, "
        f"{analytics['edge_count']} edges, "
        f"{analytics['num_communities']} communities, "
        f"{analytics['num_components']} components"
    )

    # Build serializable analytics dict for report_generator
    graph_analytics = {
        "total_nodes": analytics["node_count"],
        "total_edges": analytics["edge_count"],
        "top_entities_by_betweenness": [
            {"name": name, "score": round(score, 3)}
            for name, score in analytics.get("betweenness_centrality_top5", [])
        ],
        "top_entities_by_degree": [
            {"name": name, "score": round(score, 3)}
            for name, score in analytics.get("degree_centrality_top5", [])
        ],
        "num_communities": analytics.get("num_communities", 0),
        "largest_community_size": analytics.get("largest_component_size", 0),
        "num_connected_components": analytics.get("num_components", 0),
    }

    # Save graph DB to JSON for portability
    json_path = os.path.join(settings.output_dir, f"{safe_name}_graph.json")
    db.save(json_path)

    # --- Export to interactive HTML ---
    os.makedirs(settings.graphs_dir, exist_ok=True)
    html_path = os.path.join(settings.graphs_dir, f"{safe_name}_identity_graph.html")

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#0f172a",
        font_color="#e2e8f0",
    )
    net.from_nx(G)

    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -100,
                "centralGravity": 0.012,
                "springLength": 220,
                "springConstant": 0.05,
                "damping": 0.4
            },
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 250, "fit": true},
            "minVelocity": 0.75
        },
        "edges": {
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.6, "type": "arrow"}},
            "smooth": {"type": "curvedCW", "roundness": 0.15},
            "hoverWidth": 2,
            "selectionWidth": 2
        },
        "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "shadow": {"enabled": true, "color": "rgba(0,0,0,0.3)", "size": 8, "x": 2, "y": 2}
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 50,
            "hideEdgesOnDrag": false,
            "zoomView": true,
            "dragView": true,
            "navigationButtons": true
        }
    }
    """)

    net.save_graph(html_path)

    # Inject legend + stats overlay
    _inject_custom_styles(html_path, target_name, G.number_of_nodes(), G.number_of_edges(), len(facts))

    log_msg = (
        f"[{datetime.now().isoformat()}] GraphBuilder: "
        f"Stored {db.node_count()} entities, {db.edge_count()} relationships in graph DB → {db_path} | "
        f"Analytics: {analytics['num_communities']} communities, {analytics['num_components']} components | "
        f"Built visualization with {G.number_of_nodes()} nodes, {G.number_of_edges()} edges → {html_path}"
    )
    logger.info(log_msg)

    return {
        "graph_html": html_path,
        "graph_analytics": graph_analytics,
        "execution_log": [log_msg],
    }


def _edge_color(confidence: float) -> str:
    """Map confidence score to edge color."""
    if confidence >= 0.8:
        return "#22c55e"
    elif confidence >= 0.5:
        return "#eab308"
    else:
        return "#ef4444"


def _inject_custom_styles(html_path: str, target_name: str, num_nodes: int, num_edges: int, num_facts: int):
    """Inject a legend overlay and custom CSS into the pyvis HTML file."""
    legend_html = f"""
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; }}
        #mynetwork {{ border: none !important; }}
        .graph-legend {{
            position: fixed;
            top: 12px;
            left: 12px;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 14px 18px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #e2e8f0;
            z-index: 1000;
            min-width: 160px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        .graph-legend h3 {{
            margin: 0 0 10px 0;
            font-size: 13px;
            font-weight: 600;
            color: #f8fafc;
            letter-spacing: 0.5px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 6px 0;
            font-size: 11.5px;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex-shrink: 0;
            border: 2px solid rgba(255,255,255,0.15);
        }}
        .legend-diamond {{
            width: 10px;
            height: 10px;
            transform: rotate(45deg);
            flex-shrink: 0;
            border: 2px solid rgba(255,255,255,0.15);
        }}
        .legend-triangle {{
            width: 0; height: 0;
            border-left: 7px solid transparent;
            border-right: 7px solid transparent;
            border-bottom: 12px solid #10b981;
            flex-shrink: 0;
        }}
        .legend-square {{
            width: 10px;
            height: 10px;
            flex-shrink: 0;
            border: 2px solid rgba(255,255,255,0.15);
        }}
        .legend-star {{
            color: #ef4444;
            font-size: 16px;
            line-height: 1;
            flex-shrink: 0;
        }}
        .legend-divider {{
            border-top: 1px solid rgba(148,163,184,0.15);
            margin: 8px 0;
        }}
        .confidence-bar {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 4px 0;
            font-size: 11px;
        }}
        .conf-line {{
            width: 20px;
            height: 3px;
            border-radius: 2px;
        }}
        .graph-stats {{
            position: fixed;
            top: 12px;
            right: 12px;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 14px 18px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #e2e8f0;
            z-index: 1000;
            text-align: right;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        .graph-stats h3 {{
            margin: 0 0 8px 0;
            font-size: 13px;
            font-weight: 600;
            color: #f8fafc;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin: 4px 0;
            font-size: 11.5px;
        }}
        .stat-value {{
            font-weight: 600;
            color: #6366f1;
        }}
    </style>

    <div class="graph-legend">
        <h3>Node Types</h3>
        <div class="legend-item">
            <div class="legend-dot" style="background: #ef4444; border-color: #fbbf24;"></div>
            <span>Target</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: #6366f1;"></div>
            <span>Person</span>
        </div>
        <div class="legend-item">
            <div class="legend-diamond" style="background: #f59e0b;"></div>
            <span>Organization</span>
        </div>
        <div class="legend-item">
            <div class="legend-triangle"></div>
            <span>Event</span>
        </div>
        <div class="legend-item">
            <div class="legend-square" style="background: #8b5cf6;"></div>
            <span>Filing</span>
        </div>
        <div class="legend-item">
            <div class="legend-star">&#9733;</div>
            <span>Location</span>
        </div>
        <div class="legend-divider"></div>
        <h3>Edge Confidence</h3>
        <div class="confidence-bar">
            <div class="conf-line" style="background: #22c55e;"></div>
            <span>High (&ge; 80%)</span>
        </div>
        <div class="confidence-bar">
            <div class="conf-line" style="background: #eab308;"></div>
            <span>Medium (&ge; 50%)</span>
        </div>
        <div class="confidence-bar">
            <div class="conf-line" style="background: #ef4444;"></div>
            <span>Low (&lt; 50%)</span>
        </div>
    </div>

    <div class="graph-stats">
        <h3>{target_name}</h3>
        <div class="stat-row"><span>Nodes</span> <span class="stat-value">{num_nodes}</span></div>
        <div class="stat-row"><span>Connections</span> <span class="stat-value">{num_edges}</span></div>
        <div class="stat-row"><span>Facts</span> <span class="stat-value">{num_facts}</span></div>
    </div>
    """

    with open(html_path, "r") as f:
        html = f.read()

    # Style the navigation buttons and tooltip for dark theme
    nav_and_tooltip_css = """
    <style>
        /* Navigation buttons — dark theme */
        .vis-navigation .vis-button {
            background-color: rgba(30, 30, 30, 0.85) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 6px !important;
            backdrop-filter: blur(6px);
        }
        .vis-navigation .vis-button:hover {
            background-color: rgba(60, 60, 60, 0.9) !important;
            box-shadow: 0 0 8px rgba(249, 115, 22, 0.25);
        }
        .vis-button.vis-up, .vis-button.vis-down,
        .vis-button.vis-left, .vis-button.vis-right,
        .vis-button.vis-zoomIn, .vis-button.vis-zoomOut,
        .vis-button.vis-zoomExtends {
            background-image: none !important;
            display: flex !important;
            align-items: center;
            justify-content: center;
            width: 30px !important;
            height: 30px !important;
        }
        .vis-button.vis-up::after { content: '\\2191'; color: #d4d4d4; font-size: 16px; }
        .vis-button.vis-down::after { content: '\\2193'; color: #d4d4d4; font-size: 16px; }
        .vis-button.vis-left::after { content: '\\2190'; color: #d4d4d4; font-size: 16px; }
        .vis-button.vis-right::after { content: '\\2192'; color: #d4d4d4; font-size: 16px; }
        .vis-button.vis-zoomIn::after { content: '+'; color: #d4d4d4; font-size: 18px; font-weight: bold; }
        .vis-button.vis-zoomOut::after { content: '\\2212'; color: #d4d4d4; font-size: 18px; font-weight: bold; }
        .vis-button.vis-zoomExtends::after { content: '\\2922'; color: #d4d4d4; font-size: 16px; }

        /* Tooltip — dark theme, render HTML properly */
        div.vis-tooltip {
            background: rgba(23, 23, 23, 0.95) !important;
            border: 1px solid rgba(249, 115, 22, 0.2) !important;
            border-radius: 8px !important;
            color: #e5e5e5 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            font-size: 12px !important;
            padding: 10px 14px !important;
            backdrop-filter: blur(8px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
            max-width: 350px !important;
            line-height: 1.5 !important;
        }
        div.vis-tooltip b {
            color: #ffffff;
        }
        div.vis-tooltip i {
            color: #a3a3a3;
        }
    </style>
    """

    html = html.replace("</body>", nav_and_tooltip_css + legend_html + "\n</body>")

    with open(html_path, "w") as f:
        f.write(html)
