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
      <div className="rounded-lg border border-white/10 bg-white/5 p-8 text-center text-slate-400">
        No risk flags identified.
      </div>
    );
  }

  const sorted = [...risks].sort((a, b) => b.severity - a.severity);

  return (
    <div className="space-y-3">
      {sorted.map((risk) => (
        <div
          key={risk.id}
          className="rounded-lg border border-white/10 bg-white/5 p-4"
        >
          <div className="flex items-start gap-3">
            <div
              className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
              style={{ backgroundColor: getSeverityColor(risk.severity) }}
            >
              {risk.severity}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">
                  {SEVERITY_LABELS[risk.severity] || "UNKNOWN"}
                </span>
                <Badge
                  variant="secondary"
                  className="bg-white/10 text-xs text-slate-300"
                >
                  {risk.category}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-slate-300">{risk.description}</p>
              {risk.recommendation && (
                <p className="mt-2 text-xs text-slate-500">
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
