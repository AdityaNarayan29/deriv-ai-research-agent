"use client";

import { useState } from "react";
import type { ExtractedFact } from "@/lib/types";
import { getConfidenceColor, getConfidenceLabel } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";

interface Props {
  facts: ExtractedFact[];
}

export function FactsTab({ facts }: Props) {
  const [sortBy, setSortBy] = useState<"confidence" | "category">("confidence");

  if (!facts.length) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-8 text-center text-slate-400">
        No facts extracted.
      </div>
    );
  }

  const sorted = [...facts].sort((a, b) =>
    sortBy === "confidence"
      ? b.confidence - a.confidence
      : a.category.localeCompare(b.category)
  );

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <button
          onClick={() => setSortBy("confidence")}
          className={`rounded-full px-3 py-1 text-xs ${
            sortBy === "confidence"
              ? "bg-indigo-500/20 text-indigo-400"
              : "bg-white/5 text-slate-400"
          }`}
        >
          Sort by Confidence
        </button>
        <button
          onClick={() => setSortBy("category")}
          className={`rounded-full px-3 py-1 text-xs ${
            sortBy === "category"
              ? "bg-indigo-500/20 text-indigo-400"
              : "bg-white/5 text-slate-400"
          }`}
        >
          Sort by Category
        </button>
      </div>

      {sorted.map((fact) => (
        <div
          key={fact.id}
          className="rounded-lg border border-white/10 bg-white/5 p-4 transition-colors hover:bg-white/[.07]"
        >
          <div className="flex items-start gap-3">
            <div
              className="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: getConfidenceColor(fact.confidence) }}
              title={`${getConfidenceLabel(fact.confidence)} confidence (${Math.round(fact.confidence * 100)}%)`}
            />
            <div className="min-w-0 flex-1">
              <p className="text-sm text-slate-200">
                <span className="font-semibold text-white">{fact.subject}</span>{" "}
                {fact.predicate}{" "}
                <span className="font-semibold text-white">{fact.object}</span>
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <Badge
                  variant="secondary"
                  className="bg-white/10 text-xs text-slate-300"
                >
                  {fact.category}
                </Badge>
                <span className="text-xs text-slate-500">
                  {Math.round(fact.confidence * 100)}% confidence
                </span>
                {fact.source_url && (
                  <a
                    href={fact.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="truncate text-xs text-indigo-400 hover:underline"
                  >
                    source
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
