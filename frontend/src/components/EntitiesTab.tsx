"use client";

import type { Entity } from "@/lib/types";
import { ENTITY_CONFIG } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";

interface Props {
  entities: Entity[];
}

export function EntitiesTab({ entities }: Props) {
  if (!entities.length) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-8 text-center text-slate-400">
        No entities discovered.
      </div>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {entities.map((entity) => {
        const config = ENTITY_CONFIG[entity.entity_type];
        return (
          <div
            key={entity.id}
            className="rounded-lg border border-white/10 bg-white/5 p-4 transition-colors hover:bg-white/[.07]"
          >
            <div className="flex items-center gap-3">
              <div
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-lg"
                style={{ backgroundColor: `${config?.color || "#64748b"}20` }}
              >
                <div
                  className="h-4 w-4 rounded-full"
                  style={{ backgroundColor: config?.color || "#64748b" }}
                />
              </div>
              <div className="min-w-0">
                <p className="truncate font-semibold text-white">
                  {entity.name}
                </p>
                <Badge
                  variant="secondary"
                  className="mt-1 bg-white/10 text-xs text-slate-300"
                >
                  {config?.label || entity.entity_type}
                </Badge>
              </div>
            </div>
            {entity.description && (
              <p className="mt-3 text-xs text-slate-400 line-clamp-2">
                {entity.description}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
