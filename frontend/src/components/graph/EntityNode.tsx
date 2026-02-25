"use client";

import { memo, useRef } from "react";
import { Handle, Position } from "@xyflow/react";
import gsap from "gsap";
import type { GraphNodeData } from "./transformGraphData";

const SHAPE_CLIP_PATHS: Record<string, string> = {
  person: "circle(50%)",
  organization: "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)",
  event: "polygon(50% 0%, 100% 100%, 0% 100%)",
  filing: "inset(5% round 4px)",
  location: "polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)",
};

function EntityNodeComponent({ data }: { data: GraphNodeData }) {
  const ref = useRef<HTMLDivElement>(null);

  const onMouseEnter = () => {
    if (ref.current) gsap.to(ref.current, { scale: 1.15, duration: 0.2, ease: "power2.out" });
  };
  const onMouseLeave = () => {
    if (ref.current) gsap.to(ref.current, { scale: 1, duration: 0.2, ease: "power2.out" });
  };

  const size = Math.min(48, Math.max(32, 24 + data.factCount * 4));

  return (
    <div
      ref={ref}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className="group relative cursor-pointer"
    >
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
      <Handle type="target" position={Position.Left} className="opacity-0" />
      <Handle type="source" position={Position.Right} className="opacity-0" />

      {/* Node shape */}
      <div className="flex flex-col items-center">
        <div
          style={{
            width: size,
            height: size,
            backgroundColor: data.color,
            clipPath: SHAPE_CLIP_PATHS[data.entityType] || "circle(50%)",
            boxShadow: `0 0 12px ${data.color}40`,
            border: `2px solid ${data.borderColor}`,
          }}
          className="transition-shadow"
        />

        {/* Label */}
        <p className="mt-1.5 max-w-[120px] truncate text-center text-[11px] font-medium text-slate-200">
          {data.label}
        </p>
      </div>

      {/* Hover tooltip */}
      <div className="pointer-events-none absolute left-1/2 top-full mt-4 z-50 hidden -translate-x-1/2 whitespace-nowrap rounded-lg border border-white/10 bg-slate-800/95 px-3 py-2 text-xs backdrop-blur-sm group-hover:block">
        <p className="font-semibold text-white">{data.label}</p>
        <p className="capitalize text-slate-400">{data.entityType}</p>
        {data.description && (
          <p className="max-w-[200px] truncate text-slate-500">
            {data.description}
          </p>
        )}
        <p className="text-slate-500">
          Referenced in {data.factCount} fact(s)
        </p>
      </div>
    </div>
  );
}

export const EntityNode = memo(EntityNodeComponent);
