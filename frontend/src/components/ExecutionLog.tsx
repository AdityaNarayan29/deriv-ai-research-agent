"use client";

import { useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Props {
  logs: string[];
}

export function ExecutionLog({ logs }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length]);

  return (
    <div className="rounded-lg border border-white/10 bg-white/5">
      <div className="border-b border-white/10 px-4 py-2 text-sm font-medium text-slate-300">
        Execution Log
      </div>
      <ScrollArea className="h-64">
        <div className="space-y-0.5 p-3 font-mono text-xs">
          {logs.map((log, i) => (
            <div
              key={i}
              className={`rounded px-2 py-1 ${
                log.includes("FAILED")
                  ? "bg-red-500/10 text-red-400"
                  : log.includes("CONTINUE")
                    ? "bg-amber-500/10 text-amber-400"
                    : "text-slate-400"
              }`}
            >
              {log}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
