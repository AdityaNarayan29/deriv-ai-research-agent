"""NetworkX-backed graph database with SQLite persistence.

Default backend for development and demos. Uses NetworkX for in-memory
graph analytics and SQLite for durable storage — zero external services.
"""

import json
import sqlite3
from typing import Any

import networkx as nx
from networkx.algorithms import community as nx_community

from agent.graph_db.interface import GraphDBInterface


class NetworkXGraphDB(GraphDBInterface):
    """Graph database: NetworkX (analytics) + SQLite (persistence)."""

    def __init__(self, db_path: str | None = None):
        self._graph = nx.DiGraph()
        self._db_path = db_path
        if db_path:
            self._init_sqlite(db_path)
            self._load_from_sqlite()

    # ------ SQLite persistence ------

    def _init_sqlite(self, path: str) -> None:
        conn = sqlite3.connect(path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                properties TEXT DEFAULT '{}'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                rel_type TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                PRIMARY KEY (source_id, target_id, rel_type),
                FOREIGN KEY (source_id) REFERENCES nodes(id),
                FOREIGN KEY (target_id) REFERENCES nodes(id)
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)"
        )
        conn.commit()
        conn.close()

    def _load_from_sqlite(self) -> None:
        if not self._db_path:
            return
        conn = sqlite3.connect(self._db_path)
        for row in conn.execute(
            "SELECT id, name, entity_type, properties FROM nodes"
        ):
            props = json.loads(row[3])
            self._graph.add_node(row[0], name=row[1], entity_type=row[2], **props)
        for row in conn.execute(
            "SELECT source_id, target_id, rel_type, properties FROM edges"
        ):
            props = json.loads(row[3])
            self._graph.add_edge(row[0], row[1], rel_type=row[2], **props)
        conn.close()

    def _persist_node(
        self, entity_id: str, name: str, entity_type: str, properties: dict
    ) -> None:
        if not self._db_path:
            return
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT OR REPLACE INTO nodes (id, name, entity_type, properties) "
            "VALUES (?, ?, ?, ?)",
            (entity_id, name, entity_type, json.dumps(properties)),
        )
        conn.commit()
        conn.close()

    def _persist_edge(
        self, source_id: str, target_id: str, rel_type: str, properties: dict
    ) -> None:
        if not self._db_path:
            return
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "INSERT OR REPLACE INTO edges (source_id, target_id, rel_type, properties) "
            "VALUES (?, ?, ?, ?)",
            (source_id, target_id, rel_type, json.dumps(properties)),
        )
        conn.commit()
        conn.close()

    # ------ GraphDBInterface ------

    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        props = properties or {}
        self._graph.add_node(entity_id, name=name, entity_type=entity_type, **props)
        self._persist_node(entity_id, name, entity_type, props)

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        props = properties or {}
        self._graph.add_edge(source_id, target_id, rel_type=rel_type, **props)
        self._persist_edge(source_id, target_id, rel_type, props)

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        if entity_id not in self._graph:
            return None
        data = dict(self._graph.nodes[entity_id])
        data["id"] = entity_id
        return data

    def get_neighbors(
        self, entity_id: str, rel_type: str | None = None
    ) -> list[dict[str, Any]]:
        if entity_id not in self._graph:
            return []
        neighbors = []
        # Outgoing
        for _, target, data in self._graph.out_edges(entity_id, data=True):
            if rel_type and data.get("rel_type") != rel_type:
                continue
            node_data = dict(self._graph.nodes[target])
            node_data["id"] = target
            node_data["_edge"] = data
            neighbors.append(node_data)
        # Incoming
        for source, _, data in self._graph.in_edges(entity_id, data=True):
            if rel_type and data.get("rel_type") != rel_type:
                continue
            node_data = dict(self._graph.nodes[source])
            node_data["id"] = source
            node_data["_edge"] = data
            neighbors.append(node_data)
        return neighbors

    def shortest_path(self, source_id: str, target_id: str) -> list[str] | None:
        try:
            return nx.shortest_path(self._graph, source_id, target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def connected_components(self) -> list[list[str]]:
        undirected = self._graph.to_undirected()
        return [list(c) for c in nx.connected_components(undirected)]

    def degree_centrality(self) -> dict[str, float]:
        return nx.degree_centrality(self._graph)

    def betweenness_centrality(self) -> dict[str, float]:
        return nx.betweenness_centrality(self._graph)

    def community_detection(self) -> list[set[str]]:
        undirected = self._graph.to_undirected()
        if undirected.number_of_nodes() == 0:
            return []
        return list(nx_community.label_propagation_communities(undirected))

    def to_networkx(self) -> nx.DiGraph:
        return self._graph.copy()

    def save(self, path: str) -> None:
        data = nx.node_link_data(self._graph)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def load(self, path: str) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        self._graph = nx.node_link_graph(data, directed=True)

    def clear(self) -> None:
        self._graph.clear()
        if self._db_path:
            conn = sqlite3.connect(self._db_path)
            conn.execute("DELETE FROM edges")
            conn.execute("DELETE FROM nodes")
            conn.commit()
            conn.close()

    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        return self._graph.number_of_edges()
