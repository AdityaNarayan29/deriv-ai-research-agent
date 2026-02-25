import type { Node, Edge } from "@xyflow/react";
import type { Entity, ExtractedFact } from "@/lib/types";
import { ENTITY_CONFIG, TARGET_COLOR, TARGET_BORDER, getConfidenceColor } from "@/lib/constants";
import dagre from "@dagrejs/dagre";

export interface GraphNodeData extends Record<string, unknown> {
  label: string;
  entityType: string;
  description: string;
  factCount: number;
  isTarget: boolean;
  color: string;
  borderColor: string;
}

export interface GraphEdgeData extends Record<string, unknown> {
  label: string;
  fullLabel: string;
  confidence: number;
  factCount: number;
}

/** Fuzzy match a text string against known entity names. */
function fuzzyMatch(text: string, knownNames: Map<string, string>): string | null {
  const lower = text.toLowerCase().trim();
  // Exact match
  if (knownNames.has(lower)) return knownNames.get(lower)!;
  // Substring match
  for (const [known, canonical] of knownNames) {
    if (known.includes(lower) || lower.includes(known)) return canonical;
  }
  return null;
}

export function transformGraphData(
  targetName: string,
  entities: Entity[],
  facts: ExtractedFact[]
): { nodes: Node<GraphNodeData>[]; edges: Edge<GraphEdgeData>[] } {
  // Build known names lookup
  const knownNames = new Map<string, string>();
  knownNames.set(targetName.toLowerCase(), targetName);
  for (const e of entities) {
    knownNames.set(e.name.toLowerCase(), e.name);
  }

  // Count facts per entity
  const factCount = new Map<string, number>();
  for (const fact of facts) {
    for (const text of [fact.subject, fact.object]) {
      const match = fuzzyMatch(text, knownNames);
      if (match) factCount.set(match, (factCount.get(match) || 0) + 1);
    }
  }

  // Build nodes
  const nodes: Node<GraphNodeData>[] = [];

  // Target node
  nodes.push({
    id: targetName,
    type: "targetNode",
    position: { x: 0, y: 0 },
    data: {
      label: targetName,
      entityType: "target",
      description: "",
      factCount: factCount.get(targetName) || 0,
      isTarget: true,
      color: TARGET_COLOR,
      borderColor: TARGET_BORDER,
    },
  });

  // Entity nodes
  for (const entity of entities) {
    if (entity.name === targetName) continue;
    const config = ENTITY_CONFIG[entity.entity_type];
    nodes.push({
      id: entity.name,
      type: "entityNode",
      position: { x: 0, y: 0 },
      data: {
        label: entity.name,
        entityType: entity.entity_type,
        description: entity.description,
        factCount: factCount.get(entity.name) || 0,
        isTarget: false,
        color: config?.color || "#64748b",
        borderColor: config?.borderColor || "#475569",
      },
    });
  }

  // Build edges — group facts between same entity pairs
  const edgeMap = new Map<string, { facts: ExtractedFact[]; maxConf: number }>();

  for (const fact of facts) {
    const sourceMatch = fuzzyMatch(fact.subject, knownNames);
    const targetMatch = fuzzyMatch(fact.object, knownNames);
    if (!sourceMatch || !targetMatch || sourceMatch === targetMatch) continue;

    const key = `${sourceMatch}→${targetMatch}`;
    const existing = edgeMap.get(key);
    if (existing) {
      existing.facts.push(fact);
      existing.maxConf = Math.max(existing.maxConf, fact.confidence);
    } else {
      edgeMap.set(key, { facts: [fact], maxConf: fact.confidence });
    }
  }

  const edges: Edge<GraphEdgeData>[] = [];
  for (const [key, value] of edgeMap) {
    const [source, target] = key.split("→");
    const shortest = value.facts.reduce((a, b) =>
      a.predicate.length <= b.predicate.length ? a : b
    );
    const label =
      value.facts.length === 1
        ? shortest.predicate.slice(0, 25)
        : `${shortest.predicate.slice(0, 20)} (+${value.facts.length - 1})`;

    edges.push({
      id: key,
      source,
      target,
      type: "default",
      animated: value.maxConf >= 0.8,
      style: {
        stroke: getConfidenceColor(value.maxConf),
        strokeWidth: Math.max(1.5, value.maxConf * 3),
      },
      label,
      labelStyle: {
        fill: "#94a3b8",
        fontSize: 10,
        fontWeight: 500,
      },
      labelBgStyle: {
        fill: "#0f172a",
        fillOpacity: 0.85,
      },
      labelBgPadding: [6, 3] as [number, number],
      data: {
        label: shortest.predicate,
        fullLabel: value.facts.map((f) => f.predicate).join("; "),
        confidence: value.maxConf,
        factCount: value.facts.length,
      },
    });
  }

  // Apply dagre layout
  return applyLayout(nodes, edges);
}

function applyLayout(
  nodes: Node<GraphNodeData>[],
  edges: Edge<GraphEdgeData>[]
): { nodes: Node<GraphNodeData>[]; edges: Edge<GraphEdgeData>[] } {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({
    rankdir: "TB",
    nodesep: 80,
    ranksep: 120,
    marginx: 40,
    marginy: 40,
  });

  for (const node of nodes) {
    const w = node.data.isTarget ? 180 : 150;
    const h = node.data.isTarget ? 80 : 60;
    g.setNode(node.id, { width: w, height: h });
  }

  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  dagre.layout(g);

  const layoutNodes = nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: {
        x: pos.x - (node.data.isTarget ? 90 : 75),
        y: pos.y - (node.data.isTarget ? 40 : 30),
      },
    };
  });

  return { nodes: layoutNodes, edges };
}
