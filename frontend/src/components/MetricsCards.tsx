"use client";

import { Card, CardContent } from "@/components/ui/card";

interface Props {
  factsCount: number;
  entitiesCount: number;
  risksCount: number;
  iteration: number;
}

const metrics = [
  { key: "facts", label: "Facts Extracted", color: "text-indigo-400" },
  { key: "entities", label: "Entities Discovered", color: "text-amber-400" },
  { key: "risks", label: "Risk Flags", color: "text-red-400" },
  { key: "iteration", label: "Search Iterations", color: "text-emerald-400" },
] as const;

export function MetricsCards({
  factsCount,
  entitiesCount,
  risksCount,
  iteration,
}: Props) {
  const values: Record<string, number> = {
    facts: factsCount,
    entities: entitiesCount,
    risks: risksCount,
    iteration,
  };

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {metrics.map((m) => (
        <Card key={m.key} className="border-white/10 bg-white/5">
          <CardContent className="py-3 text-center">
            <div className={`text-3xl font-bold ${m.color}`}>
              {values[m.key]}
            </div>
            <div className="mt-1 text-xs text-slate-400">{m.label}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
