"use client";

import { memo, useRef } from "react";
import { Handle, Position } from "@xyflow/react";
import gsap from "gsap";
import type { GraphNodeData } from "./transformGraphData";

/*
 * Layout: fixed 56px circle, label hangs below via absolute positioning
 * so the node bounding box is exactly 56x56 = the circle.
 * Handles sit at edges of this 56x56 box → edges connect to circle perimeter.
 */
const SIZE = 56;

function TargetNodeComponent({ data }: { data: GraphNodeData }) {
  const ref = useRef<HTMLDivElement>(null);

  const onMouseEnter = () => {
    if (ref.current) gsap.to(ref.current, { scale: 1.1, duration: 0.2 });
  };
  const onMouseLeave = () => {
    if (ref.current) gsap.to(ref.current, { scale: 1, duration: 0.2 });
  };

  return (
    <div
      ref={ref}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className="group relative cursor-pointer"
      style={{ width: SIZE, height: SIZE }}
    >
      {/* Handles at circle edges */}
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
      <Handle type="target" position={Position.Left} className="opacity-0" />
      <Handle type="source" position={Position.Right} className="opacity-0" />

      {/* Glow ring */}
      <div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse rounded-full opacity-30 blur-md"
        style={{
          width: SIZE + 16,
          height: SIZE + 16,
          backgroundColor: data.color,
        }}
      />

      {/* Circle */}
      <div
        className="relative flex items-center justify-center rounded-full border-[3px] text-white"
        style={{
          width: SIZE,
          height: SIZE,
          backgroundColor: data.color,
          borderColor: data.borderColor,
          boxShadow: `0 0 20px ${data.color}60`,
        }}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6">
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="6" />
          <circle cx="12" cy="12" r="2" />
          <line x1="12" y1="2" x2="12" y2="6" />
          <line x1="12" y1="18" x2="12" y2="22" />
          <line x1="2" y1="12" x2="6" y2="12" />
          <line x1="18" y1="12" x2="22" y2="12" />
        </svg>
      </div>

      {/* Label — absolutely positioned below circle, outside bounding box */}
      <p
        className="absolute left-1/2 -translate-x-1/2 text-[11px] font-bold text-white whitespace-nowrap"
        style={{ top: SIZE + 4 }}
      >
        {data.label}
      </p>

      {/* Hover tooltip */}
      <div
        className="pointer-events-none absolute left-1/2 z-50 hidden -translate-x-1/2 whitespace-nowrap rounded-lg border border-orange-500/20 bg-neutral-900/95 px-3 py-2 text-xs backdrop-blur-sm group-hover:block"
        style={{ top: SIZE + 22 }}
      >
        <p className="font-semibold text-white">{data.label}</p>
        <p className="text-orange-400">Investigation Target</p>
        <p className="text-neutral-500">Referenced in {data.factCount} fact(s)</p>
      </div>
    </div>
  );
}

export const TargetNode = memo(TargetNodeComponent);
