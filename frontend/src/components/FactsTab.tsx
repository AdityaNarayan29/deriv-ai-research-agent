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
      <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-center text-sm text-neutral-400 sm:p-8">
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
    <div className="space-y-2 sm:space-y-3">
      <div className="flex flex-wrap gap-1.5 sm:gap-2">
        <button
          onClick={() => setSortBy("confidence")}
          className={`rounded-full px-2.5 py-1 text-[10px] sm:px-3 sm:text-xs ${
            sortBy === "confidence"
              ? "bg-orange-500/20 text-orange-400"
              : "bg-white/5 text-neutral-400"
          }`}
        >
          Sort by Confidence
        </button>
        <button
          onClick={() => setSortBy("category")}
          className={`rounded-full px-2.5 py-1 text-[10px] sm:px-3 sm:text-xs ${
            sortBy === "category"
              ? "bg-orange-500/20 text-orange-400"
              : "bg-white/5 text-neutral-400"
          }`}
        >
          Sort by Category
        </button>
      </div>

      {sorted.map((fact) => (
        <div
          key={fact.id}
          className="rounded-lg border border-white/10 bg-white/5 p-3 transition-colors hover:bg-white/[.07] sm:p-4"
        >
          <div className="flex items-start gap-2 sm:gap-3">
            <div
              className="mt-1 h-2 w-2 shrink-0 rounded-full sm:mt-1.5 sm:h-2.5 sm:w-2.5"
              style={{ backgroundColor: getConfidenceColor(fact.confidence) }}
              title={`${getConfidenceLabel(fact.confidence)} confidence (${Math.round(fact.confidence * 100)}%)`}
            />
            <div className="min-w-0 flex-1">
              <p className="text-xs text-neutral-200 sm:text-sm">
                <span className="font-semibold text-white">{fact.subject}</span>{" "}
                {fact.predicate}{" "}
                <span className="font-semibold text-white">{fact.object}</span>
              </p>
              <div className="mt-1.5 flex flex-wrap items-center gap-1.5 sm:mt-2 sm:gap-2">
                <Badge
                  variant="secondary"
                  className="bg-white/10 text-[10px] text-neutral-300 sm:text-xs"
                >
                  {fact.category}
                </Badge>
                <span className="text-[10px] text-neutral-500 sm:text-xs">
                  {Math.round(fact.confidence * 100)}%
                </span>
                {fact.source_url && (
                  <a
                    href={fact.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="truncate text-[10px] text-orange-400 hover:underline sm:text-xs"
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
