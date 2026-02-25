"use client";

import { memo, useRef } from "react";
import { Handle, Position } from "@xyflow/react";
import gsap from "gsap";
import type { GraphNodeData } from "./transformGraphData";

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
    >
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
      <Handle type="target" position={Position.Left} className="opacity-0" />
      <Handle type="source" position={Position.Right} className="opacity-0" />

      {/* Glow ring */}
      <div
        className="absolute -inset-2 animate-pulse rounded-full opacity-40 blur-md"
        style={{ backgroundColor: data.color }}
      />

      {/* Node body */}
      <div
        className="relative flex h-16 w-16 items-center justify-center rounded-full border-[3px] text-xs font-bold text-white"
        style={{
          backgroundColor: data.color,
          borderColor: data.borderColor,
          boxShadow: `0 0 20px ${data.color}60`,
        }}
      >
        <span className="text-center text-[10px] leading-tight px-1">
          TARGET
        </span>
      </div>

      {/* Label */}
      <div className="mt-2 text-center">
        <p className="text-xs font-bold text-white whitespace-nowrap">
          {data.label}
        </p>
        <p className="text-[10px] text-slate-400">
          {data.factCount} facts
        </p>
      </div>

      {/* Hover tooltip */}
      <div className="pointer-events-none absolute left-1/2 top-full mt-8 z-50 hidden -translate-x-1/2 rounded-lg border border-white/10 bg-slate-800/95 px-3 py-2 text-xs backdrop-blur-sm group-hover:block">
        <p className="font-semibold text-white">{data.label}</p>
        <p className="text-slate-400">Investigation Target</p>
        <p className="text-slate-500">Referenced in {data.factCount} fact(s)</p>
      </div>
    </div>
  );
}

export const TargetNode = memo(TargetNodeComponent);
