"use client";

import { useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useInvestigation } from "@/hooks/useInvestigation";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { PipelineProgress } from "@/components/PipelineProgress";
import { ExecutionLog } from "@/components/ExecutionLog";
import { MetricsCards } from "@/components/MetricsCards";
import { ReportTab } from "@/components/ReportTab";
import { FactsTab } from "@/components/FactsTab";
import { RisksTab } from "@/components/RisksTab";
import { EntitiesTab } from "@/components/EntitiesTab";
import { IdentityGraph } from "@/components/graph/IdentityGraph";

function InvestigateContent() {
  const searchParams = useSearchParams();
  const isDemo = searchParams.get("demo") === "true";
  const name = isDemo ? "Timothy Overturf" : (searchParams.get("name") || "");
  const context = isDemo ? "CEO of Sisu Capital" : (searchParams.get("context") || "");
  const iterations = parseInt(searchParams.get("iterations") || "5", 10);

  const investigation = useInvestigation();
  const started = useRef(false);

  useEffect(() => {
    if (!started.current) {
      if (isDemo) {
        started.current = true;
        investigation.startDemo();
      } else if (name) {
        started.current = true;
        investigation.start(name, context, iterations);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name, isDemo]);

  return (
    <div className="mx-auto max-w-6xl px-3 py-4 sm:px-4 sm:py-6 md:px-6 md:py-8">
      {/* Header */}
      <div className="mb-4 sm:mb-6">
        <a href="/" className="text-xs text-neutral-400 hover:text-orange-400 sm:text-sm">
          ← <span className="text-orange-500/70 font-semibold">masst spy</span>
        </a>
        <h1 className="mt-1.5 text-lg font-bold text-white sm:mt-2 sm:text-xl md:text-2xl">
          Investigating: {name}
          {isDemo && (
            <span className="ml-2 rounded bg-orange-500/20 px-1.5 py-0.5 text-[10px] font-medium text-orange-400 sm:px-2 sm:text-sm">
              DEMO
            </span>
          )}
        </h1>
        {context && <p className="text-xs text-neutral-400 sm:text-sm">{context}</p>}
      </div>

      {/* Progress Section */}
      {investigation.status === "running" && (
        <div className="mb-6 space-y-3 sm:mb-8 sm:space-y-4">
          <PipelineProgress currentNode={investigation.currentNode} />
          <Progress
            value={investigation.progress * 100}
            className="h-1.5 sm:h-2"
          />
          <MetricsCards
            factsCount={investigation.facts.length}
            entitiesCount={investigation.entities.length}
            risksCount={investigation.riskFlags.length}
            iteration={investigation.iteration}
          />
        </div>
      )}

      {/* Error */}
      {investigation.status === "error" && (
        <Card className="mb-4 border-red-500/30 bg-red-500/10 sm:mb-6">
          <CardContent className="py-3 text-sm text-red-400 sm:py-4">
            {investigation.error}
          </CardContent>
        </Card>
      )}

      {/* Execution Log (always visible during running) */}
      {investigation.status === "running" && (
        <div className="mb-6 sm:mb-8">
          <ExecutionLog logs={investigation.logs} />
        </div>
      )}

      {/* Results */}
      {investigation.status === "complete" && (
        <>
          <MetricsCards
            factsCount={investigation.facts.length}
            entitiesCount={investigation.entities.length}
            risksCount={investigation.riskFlags.length}
            iteration={investigation.iteration}
          />

          <Tabs defaultValue="graph" className="mt-4 sm:mt-6">
            <TabsList className="w-full overflow-x-auto border-white/10 bg-white/5 flex-nowrap justify-start sm:justify-center">
              <TabsTrigger value="graph" className="text-xs sm:text-sm">Graph</TabsTrigger>
              <TabsTrigger value="report" className="text-xs sm:text-sm">Report</TabsTrigger>
              <TabsTrigger value="facts" className="text-xs sm:text-sm">
                Facts ({investigation.facts.length})
              </TabsTrigger>
              <TabsTrigger value="risks" className="text-xs sm:text-sm">
                Risks ({investigation.riskFlags.length})
              </TabsTrigger>
              <TabsTrigger value="entities" className="text-xs sm:text-sm">
                Entities ({investigation.entities.length})
              </TabsTrigger>
              <TabsTrigger value="log" className="text-xs sm:text-sm">Log</TabsTrigger>
            </TabsList>

            <TabsContent value="graph" className="mt-3 sm:mt-4">
              <IdentityGraph
                targetName={name}
                entities={investigation.entities}
                facts={investigation.facts}
              />
            </TabsContent>

            <TabsContent value="report" className="mt-3 sm:mt-4">
              <ReportTab report={investigation.report} />
            </TabsContent>

            <TabsContent value="facts" className="mt-3 sm:mt-4">
              <FactsTab facts={investigation.facts} />
            </TabsContent>

            <TabsContent value="risks" className="mt-3 sm:mt-4">
              <RisksTab risks={investigation.riskFlags} />
            </TabsContent>

            <TabsContent value="entities" className="mt-3 sm:mt-4">
              <EntitiesTab entities={investigation.entities} />
            </TabsContent>

            <TabsContent value="log" className="mt-3 sm:mt-4">
              <ExecutionLog logs={investigation.logs} />
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}

export default function InvestigatePage() {
  return (
    <Suspense fallback={<div className="p-4 text-neutral-400 sm:p-8">Loading...</div>}>
      <InvestigateContent />
    </Suspense>
  );
}
