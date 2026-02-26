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
      <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-center text-sm text-neutral-400 sm:p-8">
        No entities discovered.
      </div>
    );
  }

  return (
    <div className="grid gap-2 grid-cols-1 sm:grid-cols-2 sm:gap-3 lg:grid-cols-3">
      {entities.map((entity) => {
        const config = ENTITY_CONFIG[entity.entity_type];
        return (
          <div
            key={entity.id}
            className="rounded-lg border border-white/10 bg-white/5 p-3 transition-colors hover:bg-white/[.07] sm:p-4"
          >
            <div className="flex items-center gap-2 sm:gap-3">
              <div
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg sm:h-10 sm:w-10"
                style={{ backgroundColor: `${config?.color || "#64748b"}20` }}
              >
                <div
                  className="h-3 w-3 rounded-full sm:h-4 sm:w-4"
                  style={{ backgroundColor: config?.color || "#64748b" }}
                />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">
                  {entity.name}
                </p>
                <Badge
                  variant="secondary"
                  className="mt-0.5 bg-white/10 text-[10px] text-neutral-300 sm:mt-1 sm:text-xs"
                >
                  {config?.label || entity.entity_type}
                </Badge>
              </div>
            </div>
            {entity.description && (
              <p className="mt-2 text-[10px] text-neutral-400 line-clamp-2 sm:mt-3 sm:text-xs">
                {entity.description}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
