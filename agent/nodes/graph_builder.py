"""Node 6: Graph Builder — builds identity graph using NetworkX + pyvis.

Generates an interactive HTML visualization of the identity network,
with color-coded nodes by type and edge weights by confidence.
"""

import os
import logging
from datetime import datetime

import networkx as nx
from pyvis.network import Network

from config.settings import settings
from agent.state import AgentState, EntityType

logger = logging.getLogger(__name__)

# Color scheme for entity types
NODE_COLORS = {
    EntityType.PERSON: "#4A90D9",        # Blue
    EntityType.ORGANIZATION: "#E67E22",  # Orange
    EntityType.EVENT: "#27AE60",         # Green
    EntityType.FILING: "#8E44AD",        # Purple
    EntityType.LOCATION: "#E74C3C",      # Red
}

NODE_SHAPES = {
    EntityType.PERSON: "dot",
    EntityType.ORGANIZATION: "diamond",
    EntityType.EVENT: "triangle",
    EntityType.FILING: "square",
    EntityType.LOCATION: "star",
}


def graph_builder(state: AgentState) -> dict:
    """Build a NetworkX identity graph and export to interactive HTML.

    Creates nodes for all entities and edges for all relationship facts,
    with visual properties reflecting entity types and confidence levels.
    """
    entities = state.get("entities", [])
    facts = state.get("facts", [])
    target_name = state["target_name"]

    if not entities and not facts:
        return {
            "execution_log": [f"[{datetime.now().isoformat()}] GraphBuilder: No entities or facts to graph"],
        }

    G = nx.DiGraph()

    # Add target as the central node
    G.add_node(
        target_name,
        title=f"TARGET: {target_name}\n{state.get('target_context', '')}",
        color="#FF6B6B",  # Highlight color for target
        size=40,
        shape="dot",
        font={"size": 16, "bold": True},
    )

    # Add entity nodes
    entity_lookup = {e.name.lower(): e for e in entities}
    for entity in entities:
        G.add_node(
            entity.name,
            title=f"{entity.entity_type.value}: {entity.description}",
            color=NODE_COLORS.get(entity.entity_type, "#95A5A6"),
            size=25,
            shape=NODE_SHAPES.get(entity.entity_type, "dot"),
        )

    # Add edges from facts (subject → object relationships)
    for fact in facts:
        source = fact.subject
        target = fact.object

        # Only add edges where both nodes exist or can be created
        if not G.has_node(source):
            G.add_node(source, title=source, color="#95A5A6", size=15, shape="dot")
        if not G.has_node(target):
            G.add_node(target, title=target, color="#95A5A6", size=15, shape="dot")

        # Edge width based on confidence
        width = max(1, fact.confidence * 5)
        G.add_edge(
            source,
            target,
            title=f"{fact.predicate}\nConfidence: {fact.confidence:.0%}\nCategory: {fact.category.value}",
            label=fact.predicate[:30],  # Truncate long labels
            width=width,
            color=_edge_color(fact.confidence),
        )

    # Export to interactive HTML using pyvis
    os.makedirs(settings.graphs_dir, exist_ok=True)
    safe_name = target_name.replace(" ", "_").replace(",", "")[:50]
    html_path = os.path.join(settings.graphs_dir, f"{safe_name}_identity_graph.html")

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#1a1a2e",
        font_color="white",
    )
    net.from_nx(G)

    # Physics settings for better layout
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 200,
                "springConstant": 0.08
            },
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 150}
        },
        "edges": {
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
            "smooth": {"type": "curvedCW", "roundness": 0.2}
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)

    net.save_graph(html_path)

    log_msg = (
        f"[{datetime.now().isoformat()}] GraphBuilder: "
        f"Built graph with {G.number_of_nodes()} nodes, {G.number_of_edges()} edges → {html_path}"
    )
    logger.info(log_msg)

    return {
        "graph_html": html_path,
        "execution_log": [log_msg],
    }


def _edge_color(confidence: float) -> str:
    """Map confidence score to edge color."""
    if confidence >= 0.8:
        return "#2ECC71"  # Green — high confidence
    elif confidence >= 0.5:
        return "#F39C12"  # Yellow — medium confidence
    else:
        return "#E74C3C"  # Red — low confidence
