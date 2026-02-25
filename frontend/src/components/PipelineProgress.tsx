"use client";

import { PIPELINE_NODES } from "@/lib/constants";

interface Props {
  currentNode: string;
}

export function PipelineProgress({ currentNode }: Props) {
  const currentIndex = PIPELINE_NODES.findIndex((n) => n.key === currentNode);

  return (
    <div className="flex items-center gap-1 overflow-x-auto py-2">
      {PIPELINE_NODES.map((node, i) => {
        const isActive = node.key === currentNode;
        const isDone = i < currentIndex;

        return (
          <div key={node.key} className="flex items-center">
            <div className="flex flex-col items-center gap-1">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all duration-300 ${
                  isActive
                    ? "animate-pulse bg-indigo-500 text-white ring-2 ring-indigo-400 ring-offset-2 ring-offset-[#0f172a]"
                    : isDone
                      ? "bg-emerald-500/20 text-emerald-400"
                      : "bg-white/5 text-slate-500"
                }`}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <span
                className={`whitespace-nowrap text-[10px] ${
                  isActive
                    ? "font-semibold text-indigo-400"
                    : isDone
                      ? "text-emerald-400/60"
                      : "text-slate-600"
                }`}
              >
                {node.label}
              </span>
            </div>
            {i < PIPELINE_NODES.length - 1 && (
              <div
                className={`mx-1 h-px w-6 ${
                  isDone ? "bg-emerald-500/40" : "bg-white/10"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
