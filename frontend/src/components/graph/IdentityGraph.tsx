"use client";

import { useMemo, useCallback, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { Entity, ExtractedFact } from "@/lib/types";
import { ENTITY_CONFIG } from "@/lib/constants";
import { transformGraphData } from "./transformGraphData";
import { TargetNode } from "./TargetNode";
import { EntityNode } from "./EntityNode";
import { useGraphAnimations } from "./useGraphAnimations";

interface Props {
  targetName: string;
  entities: Entity[];
  facts: ExtractedFact[];
}

const nodeTypes: NodeTypes = {
  targetNode: TargetNode,
  entityNode: EntityNode,
};

export function IdentityGraph({ targetName, entities, facts }: Props) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => transformGraphData(targetName, entities, facts),
    [targetName, entities, facts]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useGraphAnimations(nodes.length, edges.length);

  // Click node: highlight connected, dim others
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (selectedNode === node.id) {
        // Deselect: reset all
        setSelectedNode(null);
        setNodes((nds) => nds.map((n) => ({ ...n, style: { ...n.style, opacity: 1 } })));
        setEdges((eds) => eds.map((e) => ({ ...e, style: { ...e.style, opacity: 1 } })));
        return;
      }

      setSelectedNode(node.id);

      // Find connected node IDs
      const connectedIds = new Set<string>([node.id]);
      for (const edge of edges) {
        if (edge.source === node.id) connectedIds.add(edge.target);
        if (edge.target === node.id) connectedIds.add(edge.source);
      }

      // Dim non-connected
      setNodes((nds) =>
        nds.map((n) => ({
          ...n,
          style: { ...n.style, opacity: connectedIds.has(n.id) ? 1 : 0.15 },
        }))
      );
      setEdges((eds) =>
        eds.map((e) => ({
          ...e,
          style: {
            ...e.style,
            opacity: e.source === node.id || e.target === node.id ? 1 : 0.1,
          },
        }))
      );
    },
    [selectedNode, edges, setNodes, setEdges]
  );

  // Click background: reset
  const onPaneClick = useCallback(() => {
    if (selectedNode) {
      setSelectedNode(null);
      setNodes((nds) => nds.map((n) => ({ ...n, style: { ...n.style, opacity: 1 } })));
      setEdges((eds) => eds.map((e) => ({ ...e, style: { ...e.style, opacity: 1 } })));
    }
  }, [selectedNode, setNodes, setEdges]);

  if (!entities.length && !facts.length) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-8 text-center text-slate-400">
        No graph data available.
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden rounded-lg border border-white/10">
      {/* Legend */}
      <div className="absolute left-3 top-3 z-10 rounded-lg border border-white/10 bg-slate-900/90 p-3 text-xs backdrop-blur-sm">
        <p className="mb-2 font-semibold text-slate-200">Node Types</p>
        {Object.entries(ENTITY_CONFIG).map(([type, config]) => (
          <div key={type} className="flex items-center gap-2 py-0.5">
            <div
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: config.color }}
            />
            <span className="text-slate-400">{config.label}</span>
          </div>
        ))}
        <div className="flex items-center gap-2 py-0.5">
          <div className="h-3 w-3 rounded-full bg-red-500 ring-1 ring-amber-400" />
          <span className="text-slate-400">Target</span>
        </div>
        <div className="mt-2 border-t border-white/10 pt-2">
          <p className="mb-1 font-semibold text-slate-200">Edge Confidence</p>
          <div className="flex items-center gap-2 py-0.5">
            <div className="h-0.5 w-4 rounded bg-emerald-500" />
            <span className="text-slate-400">High</span>
          </div>
          <div className="flex items-center gap-2 py-0.5">
            <div className="h-0.5 w-4 rounded bg-yellow-500" />
            <span className="text-slate-400">Medium</span>
          </div>
          <div className="flex items-center gap-2 py-0.5">
            <div className="h-0.5 w-4 rounded bg-red-500" />
            <span className="text-slate-400">Low</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="absolute right-3 top-3 z-10 rounded-lg border border-white/10 bg-slate-900/90 px-3 py-2 text-xs backdrop-blur-sm">
        <p className="font-semibold text-slate-200">{targetName}</p>
        <p className="text-slate-400">{nodes.length} nodes</p>
        <p className="text-slate-400">{edges.length} connections</p>
        <p className="text-slate-400">{facts.length} facts</p>
      </div>

      <div style={{ height: 700 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.3}
          maxZoom={2}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1e293b" gap={20} />
          <Controls
            className="rounded-lg border border-white/10 bg-slate-900/90"
            showInteractive={false}
          />
          <MiniMap
            nodeColor={(node) => {
              if (node.data?.isTarget) return "#ef4444";
              return (node.data?.color as string) || "#64748b";
            }}
            maskColor="rgba(15, 23, 42, 0.8)"
            className="rounded-lg border border-white/10"
            style={{ backgroundColor: "#0f172a" }}
          />
        </ReactFlow>
      </div>
    </div>
  );
}
