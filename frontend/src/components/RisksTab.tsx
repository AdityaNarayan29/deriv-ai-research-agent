"use client";

import type { RiskFlag } from "@/lib/types";
import { getSeverityColor } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";

interface Props {
  risks: RiskFlag[];
}

const SEVERITY_LABELS: Record<number, string> = {
  1: "LOW",
  2: "MODERATE",
  3: "ELEVATED",
  4: "HIGH",
  5: "CRITICAL",
};

export function RisksTab({ risks }: Props) {
  if (!risks.length) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-center text-sm text-neutral-400 sm:p-8">
        No risk flags identified.
      </div>
    );
  }

  const sorted = [...risks].sort((a, b) => b.severity - a.severity);

  return (
    <div className="space-y-2 sm:space-y-3">
      {sorted.map((risk) => (
        <div
          key={risk.id}
          className="rounded-lg border border-white/10 bg-white/5 p-3 sm:p-4"
        >
          <div className="flex items-start gap-2 sm:gap-3">
            <div
              className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white sm:h-8 sm:w-8 sm:text-sm"
              style={{ backgroundColor: getSeverityColor(risk.severity) }}
            >
              {risk.severity}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                <span className="text-xs font-semibold text-white sm:text-sm">
                  {SEVERITY_LABELS[risk.severity] || "UNKNOWN"}
                </span>
                <Badge
                  variant="secondary"
                  className="bg-white/10 text-[10px] text-neutral-300 sm:text-xs"
                >
                  {risk.category}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-neutral-300 sm:text-sm">{risk.description}</p>
              {risk.recommendation && (
                <p className="mt-1.5 text-[10px] text-neutral-500 sm:mt-2 sm:text-xs">
                  → {risk.recommendation}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
