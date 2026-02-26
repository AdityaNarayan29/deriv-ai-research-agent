"""Graph database package for identity graph storage and analytics.

Use get_graph_db() to get the configured backend.
Defaults to NetworkXGraphDB (no external services required).
"""

from agent.graph_db.interface import GraphDBInterface
from agent.graph_db.networkx_backend import NetworkXGraphDB


def get_graph_db(
    backend: str = "networkx",
    db_path: str | None = None,
    **kwargs,
) -> GraphDBInterface:
    """Factory function to create a graph database instance.

    Args:
        backend: "networkx" (default) or "neo4j" (future)
        db_path: Path for SQLite persistence (NetworkX backend)
    """
    if backend == "networkx":
        return NetworkXGraphDB(db_path=db_path)
    elif backend == "neo4j":
        raise NotImplementedError(
            "Neo4j backend not yet implemented. "
            "Install neo4j driver and configure NEO4J_URI in .env"
        )
    else:
        raise ValueError(f"Unknown graph DB backend: {backend}")


__all__ = ["GraphDBInterface", "NetworkXGraphDB", "get_graph_db"]
