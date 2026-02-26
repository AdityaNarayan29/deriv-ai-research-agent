"""Graph analytics for investigation reports.

Computes centrality, community, and connectivity metrics
using the GraphDBInterface.
"""

from agent.graph_db.interface import GraphDBInterface


def compute_investigation_analytics(db: GraphDBInterface) -> dict:
    """Compute all analytics for an investigation graph.

    Returns a dictionary of metrics for inclusion in reports
    and the frontend stats overlay.
    """
    analytics = {
        "node_count": db.node_count(),
        "edge_count": db.edge_count(),
    }

    # Centrality — find most connected / influential entities
    degree = db.degree_centrality()
    betweenness = db.betweenness_centrality()

    analytics["degree_centrality_top5"] = sorted(
        degree.items(), key=lambda x: x[1], reverse=True
    )[:5]
    analytics["betweenness_centrality_top5"] = sorted(
        betweenness.items(), key=lambda x: x[1], reverse=True
    )[:5]

    # Connected components — identify isolated clusters
    components = db.connected_components()
    analytics["num_components"] = len(components)
    analytics["largest_component_size"] = (
        max(len(c) for c in components) if components else 0
    )

    # Community detection
    communities = db.community_detection()
    analytics["num_communities"] = len(communities)
    analytics["community_sizes"] = [len(c) for c in communities]

    return analytics
