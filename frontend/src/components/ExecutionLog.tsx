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
      <div className="border-b border-white/10 px-3 py-1.5 text-xs font-medium text-neutral-300 sm:px-4 sm:py-2 sm:text-sm">
        Execution Log
      </div>
      <ScrollArea className="h-48 sm:h-64">
        <div className="space-y-0.5 p-2 font-mono text-[10px] sm:p-3 sm:text-xs">
          {logs.map((log, i) => (
            <div
              key={i}
              className={`break-all rounded px-1.5 py-0.5 sm:break-normal sm:px-2 sm:py-1 ${
                log.includes("FAILED")
                  ? "bg-red-500/10 text-red-400"
                  : log.includes("CONTINUE")
                    ? "bg-amber-500/10 text-amber-400"
                    : "text-neutral-500"
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
