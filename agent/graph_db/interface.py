"""Abstract graph database interface.

Defines the contract any graph DB backend must satisfy.
Allows swapping NetworkX (dev/demo) for Neo4j (production)
without changing application code.
"""

from abc import ABC, abstractmethod
from typing import Any


class GraphDBInterface(ABC):
    """Abstract interface for the identity graph database."""

    @abstractmethod
    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Add an entity (node) to the graph."""

    @abstractmethod
    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Add a relationship (edge) between two entities."""

    @abstractmethod
    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        """Retrieve an entity by ID."""

    @abstractmethod
    def get_neighbors(
        self, entity_id: str, rel_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all entities connected to the given entity."""

    @abstractmethod
    def shortest_path(self, source_id: str, target_id: str) -> list[str] | None:
        """Find shortest path between two entities."""

    @abstractmethod
    def connected_components(self) -> list[list[str]]:
        """Find all connected components in the graph."""

    @abstractmethod
    def degree_centrality(self) -> dict[str, float]:
        """Calculate degree centrality for all nodes."""

    @abstractmethod
    def betweenness_centrality(self) -> dict[str, float]:
        """Calculate betweenness centrality for all nodes."""

    @abstractmethod
    def community_detection(self) -> list[set[str]]:
        """Detect communities using label propagation."""

    @abstractmethod
    def to_networkx(self) -> Any:
        """Export the graph as a NetworkX DiGraph (for visualization)."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist the graph to JSON."""

    @abstractmethod
    def load(self, path: str) -> None:
        """Load the graph from JSON."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all nodes and edges."""

    @abstractmethod
    def node_count(self) -> int:
        """Return the number of nodes."""

    @abstractmethod
    def edge_count(self) -> int:
        """Return the number of edges."""
