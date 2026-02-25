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
  const name = searchParams.get("name") || "";
  const context = searchParams.get("context") || "";
  const iterations = parseInt(searchParams.get("iterations") || "5", 10);

  const investigation = useInvestigation();
  const started = useRef(false);

  useEffect(() => {
    if (name && !started.current) {
      started.current = true;
      investigation.start(name, context, iterations);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <a href="/" className="text-sm text-slate-400 hover:text-white">
          ← Back
        </a>
        <h1 className="mt-2 text-2xl font-bold text-white">
          Investigating: {name}
        </h1>
        {context && <p className="text-sm text-slate-400">{context}</p>}
      </div>

      {/* Progress Section */}
      {investigation.status === "running" && (
        <div className="mb-8 space-y-4">
          <PipelineProgress currentNode={investigation.currentNode} />
          <Progress
            value={investigation.progress * 100}
            className="h-2"
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
        <Card className="mb-6 border-red-500/30 bg-red-500/10">
          <CardContent className="py-4 text-red-400">
            {investigation.error}
          </CardContent>
        </Card>
      )}

      {/* Execution Log (always visible during running) */}
      {investigation.status === "running" && (
        <div className="mb-8">
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

          <Tabs defaultValue="graph" className="mt-6">
            <TabsList className="border-white/10 bg-white/5">
              <TabsTrigger value="graph">Identity Graph</TabsTrigger>
              <TabsTrigger value="report">Report</TabsTrigger>
              <TabsTrigger value="facts">
                Facts ({investigation.facts.length})
              </TabsTrigger>
              <TabsTrigger value="risks">
                Risks ({investigation.riskFlags.length})
              </TabsTrigger>
              <TabsTrigger value="entities">
                Entities ({investigation.entities.length})
              </TabsTrigger>
              <TabsTrigger value="log">Log</TabsTrigger>
            </TabsList>

            <TabsContent value="graph" className="mt-4">
              <IdentityGraph
                targetName={name}
                entities={investigation.entities}
                facts={investigation.facts}
              />
            </TabsContent>

            <TabsContent value="report" className="mt-4">
              <ReportTab report={investigation.report} />
            </TabsContent>

            <TabsContent value="facts" className="mt-4">
              <FactsTab facts={investigation.facts} />
            </TabsContent>

            <TabsContent value="risks" className="mt-4">
              <RisksTab risks={investigation.riskFlags} />
            </TabsContent>

            <TabsContent value="entities" className="mt-4">
              <EntitiesTab entities={investigation.entities} />
            </TabsContent>

            <TabsContent value="log" className="mt-4">
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
    <Suspense fallback={<div className="p-8 text-slate-400">Loading...</div>}>
      <InvestigateContent />
    </Suspense>
  );
}
