"use client";

import { memo, useRef } from "react";
import { Handle, Position } from "@xyflow/react";
import gsap from "gsap";
import type { GraphNodeData } from "./transformGraphData";

const ENTITY_ICONS: Record<string, React.ReactNode> = {
  person: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  ),
  organization: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
      <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
      <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
      <line x1="12" y1="12" x2="12" y2="12.01" />
    </svg>
  ),
  event: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  ),
  filing: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  ),
  location: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  ),
};

/*
 * Layout: fixed 40px circle, label hangs below via absolute positioning
 * so the node bounding box is exactly 40x40 = the circle.
 * Handles sit at edges of this 40x40 box → edges connect to circle perimeter.
 * Label is absolutely positioned below, outside the bounding box.
 */
const SIZE = 40;

function EntityNodeComponent({ data }: { data: GraphNodeData }) {
  const ref = useRef<HTMLDivElement>(null);

  const onMouseEnter = () => {
    if (ref.current) gsap.to(ref.current, { scale: 1.15, duration: 0.2, ease: "power2.out" });
  };
  const onMouseLeave = () => {
    if (ref.current) gsap.to(ref.current, { scale: 1, duration: 0.2, ease: "power2.out" });
  };

  const icon = ENTITY_ICONS[data.entityType];

  return (
    <div
      ref={ref}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className="group relative cursor-pointer"
      style={{ width: SIZE, height: SIZE }}
    >
      {/* Handles at circle edges — top/bottom/left/right of the 40x40 box */}
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
      <Handle type="target" position={Position.Left} className="opacity-0" />
      <Handle type="source" position={Position.Right} className="opacity-0" />

      {/* Circle with icon */}
      <div
        className="flex items-center justify-center rounded-full text-white/90"
        style={{
          width: SIZE,
          height: SIZE,
          backgroundColor: data.color,
          boxShadow: `0 0 12px ${data.color}60`,
        }}
      >
        {icon && (
          <div style={{ filter: "drop-shadow(0 1px 1px rgba(0,0,0,0.4))" }}>
            {icon}
          </div>
        )}
      </div>

      {/* Label — absolutely positioned below circle, outside bounding box */}
      <p
        className="absolute left-1/2 -translate-x-1/2 max-w-24 truncate text-center text-[10px] font-medium text-neutral-200 leading-tight whitespace-nowrap"
        style={{ top: SIZE + 4 }}
      >
        {data.label}
      </p>

      {/* Hover tooltip */}
      <div
        className="pointer-events-none absolute left-1/2 z-50 hidden -translate-x-1/2 whitespace-nowrap rounded-lg border border-orange-500/20 bg-neutral-900/95 px-3 py-2 text-xs backdrop-blur-sm group-hover:block"
        style={{ top: SIZE + 20 }}
      >
        <p className="font-semibold text-white">{data.label}</p>
        <p className="capitalize text-orange-400/80">{data.entityType}</p>
        {data.description && (
          <p className="max-w-[200px] truncate text-neutral-500">
            {data.description}
          </p>
        )}
        <p className="text-neutral-500">
          Referenced in {data.factCount} fact(s)
        </p>
      </div>
    </div>
  );
}

export const EntityNode = memo(EntityNodeComponent);
