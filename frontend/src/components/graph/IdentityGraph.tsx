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
      <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-center text-sm text-neutral-400 sm:p-8">
        No graph data available.
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden rounded-lg border border-white/10">
      {/* Legend — hidden on very small screens, compact on mobile */}
      <div className="absolute left-2 top-2 z-10 hidden rounded-lg border border-white/10 bg-neutral-950/90 p-2 text-[9px] backdrop-blur-sm sm:block sm:left-3 sm:top-3 sm:p-3 sm:text-xs">
        <p className="mb-1.5 font-semibold text-neutral-200 sm:mb-2">Node Types</p>
        {Object.entries(ENTITY_CONFIG).map(([type, config]) => (
          <div key={type} className="flex items-center gap-1.5 py-0.5 sm:gap-2">
            <div
              className="h-2.5 w-2.5 rounded-full sm:h-3 sm:w-3"
              style={{ backgroundColor: config.color }}
            />
            <span className="text-neutral-400">{config.label}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 py-0.5 sm:gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-red-500 ring-1 ring-amber-400 sm:h-3 sm:w-3" />
          <span className="text-neutral-400">Target</span>
        </div>
        <div className="mt-1.5 border-t border-white/10 pt-1.5 sm:mt-2 sm:pt-2">
          <p className="mb-1 font-semibold text-neutral-200">Edge Confidence</p>
          <div className="flex items-center gap-1.5 py-0.5 sm:gap-2">
            <div className="h-0.5 w-3 rounded bg-emerald-500 sm:w-4" />
            <span className="text-neutral-400">High</span>
          </div>
          <div className="flex items-center gap-1.5 py-0.5 sm:gap-2">
            <div className="h-0.5 w-3 rounded bg-yellow-500 sm:w-4" />
            <span className="text-neutral-400">Medium</span>
          </div>
          <div className="flex items-center gap-1.5 py-0.5 sm:gap-2">
            <div className="h-0.5 w-3 rounded bg-red-500 sm:w-4" />
            <span className="text-neutral-400">Low</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="absolute right-2 top-2 z-10 rounded-lg border border-orange-500/20 bg-neutral-950/90 px-2 py-1.5 text-[9px] backdrop-blur-sm sm:right-3 sm:top-3 sm:px-3 sm:py-2 sm:text-xs">
        <p className="font-semibold text-orange-400">{targetName}</p>
        <p className="text-neutral-400">{nodes.length} nodes</p>
        <p className="text-neutral-400">{edges.length} connections</p>
        <p className="text-neutral-400">{facts.length} facts</p>
      </div>

      <div className="h-[350px] sm:h-[500px] md:h-[600px] lg:h-[650px]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          minZoom={0.2}
          maxZoom={2}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1a1a1a" gap={20} />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(node) => {
              if (node.data?.isTarget) return "#ef4444";
              return (node.data?.color as string) || "#64748b";
            }}
            nodeStrokeWidth={0}
            nodeBorderRadius={50}
            maskColor="rgba(10, 10, 10, 0.7)"
            className="hidden rounded-lg border border-white/10 sm:block"
            style={{ backgroundColor: "#141414" }}
          />
        </ReactFlow>
      </div>
    </div>
  );
}
