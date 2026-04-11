"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";

/* ------------------------------------------------------------------ */
/*  Pipeline steps for the "How it works" section                      */
/* ------------------------------------------------------------------ */
const PIPELINE_STEPS = [
  {
    step: "01",
    title: "Query Planning",
    description:
      "Analyzes the target and generates diverse search queries across biographical, professional, financial, legal, and regulatory categories.",
    tech: "Groq Llama 3.3-70B",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    step: "02",
    title: "Web Search",
    description:
      "Executes queries concurrently via Tavily API with advanced depth, returning top results per query with deduplication.",
    tech: "Tavily API",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    step: "03",
    title: "Fact Extraction",
    description:
      "Extracts structured subject-predicate-object triples with confidence scores, categories, and source URLs.",
    tech: "Groq Llama 3.3-70B",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9zm3.75 11.625a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    step: "04",
    title: "Risk Analysis",
    description:
      "Cross-references all facts to identify red flags across regulatory, reputational, financial, legal, and inconsistency categories.",
    tech: "Gemini 2.0 Flash",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    step: "05",
    title: "Adaptive Refinement",
    description:
      "Evaluates gaps, uninvestigated entities, and low-confidence facts. Loops back for deeper investigation or finalizes.",
    tech: "Groq Llama 3.3-70B",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    step: "06",
    title: "Identity Graph",
    description:
      "Builds an interactive network graph mapping all entities and relationships, stored in a graph database with analytics.",
    tech: "NetworkX + SQLite",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    step: "07",
    title: "Report Generation",
    description:
      "Synthesizes a comprehensive due diligence risk assessment report with all facts, entities, and risk analysis.",
    tech: "Gemini 2.0 Flash",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

const FEATURES = [
  {
    title: "Multi-Model AI",
    description: "Groq Llama 3.3-70B for speed, Gemini 2.0 Flash for depth — with automatic fallback between providers.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: "Adaptive Search Loop",
    description: "Iteratively refines queries based on gaps in coverage, uninvestigated entities, and low-confidence facts.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: "Structured Intelligence",
    description: "Extracts facts as subject-predicate-object triples with confidence scores, source URLs, and categories.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: "Risk Assessment",
    description: "Automated detection of regulatory, reputational, financial, legal red flags with severity ratings.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: "Graph Database",
    description: "NetworkX + SQLite graph database with centrality analysis, community detection, and persistent storage.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: "Real-time Streaming",
    description: "Watch the investigation unfold live via SSE — facts, entities, and risks appear as the agent discovers them.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-5 w-5">
        <path d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

const TECH_STACK = [
  { name: "LangGraph", role: "Agent orchestration" },
  { name: "Groq", role: "Fast inference (Llama 3.3-70B)" },
  { name: "Gemini", role: "Deep analysis (2.0 Flash)" },
  { name: "Tavily", role: "Web search API" },
  { name: "FastAPI", role: "SSE streaming backend" },
  { name: "Next.js", role: "React frontend" },
  { name: "React Flow", role: "Identity graph" },
  { name: "LangSmith", role: "Observability & tracing" },
];

const STATS = [
  { value: "45+", label: "Facts per investigation" },
  { value: "26+", label: "Entities discovered" },
  { value: "7", label: "Pipeline stages" },
  { value: "3", label: "AI models" },
];

/* ------------------------------------------------------------------ */
/*  Page component                                                      */
/* ------------------------------------------------------------------ */
export default function Home() {
  const router = useRouter();
  const [targetName, setTargetName] = useState("Timothy Overturf");
  const [targetContext, setTargetContext] = useState("CEO of Sisu Capital");
  const [maxIterations, setMaxIterations] = useState(5);

  const handleStart = () => {
    if (!targetName.trim()) return;
    const params = new URLSearchParams({
      name: targetName,
      context: targetContext,
      iterations: String(maxIterations),
    });
    router.push(`/investigate?${params.toString()}`);
  };

  return (
    <div className="min-h-screen">
      {/* ── HERO ─────────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        {/* Background gradients */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-0 -translate-x-1/2 h-[500px] w-[700px] rounded-full bg-orange-500/[0.04] blur-[100px]" />
          <div className="absolute right-0 top-1/3 h-[300px] w-[400px] rounded-full bg-orange-600/[0.03] blur-[80px]" />
        </div>

        <div className="relative mx-auto flex max-w-6xl flex-col items-center gap-10 px-4 pb-16 pt-12 sm:px-6 md:pb-24 md:pt-20 lg:flex-row lg:items-start lg:gap-16 lg:pt-28">
          {/* Left — headline */}
          <div className="flex-1 text-center lg:text-left">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-orange-500/20 bg-orange-500/10 px-3 py-1 text-[11px] font-medium text-orange-400 sm:px-4 sm:py-1.5 sm:text-xs">
              <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse" />
              Autonomous AI Research Agent
            </div>

            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl lg:text-6xl">
              <span className="text-orange-500">masst</span> spy
            </h1>
            <p className="mt-2 text-sm font-medium tracking-wide text-neutral-500 uppercase sm:text-base">
              AI-Powered Due Diligence Research Agent
            </p>

            <p className="mx-auto mt-4 max-w-lg text-base leading-relaxed text-neutral-400 sm:mt-6 sm:text-lg lg:mx-0">
              Enter a name, and our autonomous agent investigates across the web
              — extracting facts, mapping relationships, flagging risks, and
              generating a comprehensive report. All in real-time.
            </p>

            {/* Stats row */}
            <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4 lg:max-w-lg">
              {STATS.map((s) => (
                <div key={s.label} className="rounded-lg border border-white/5 bg-white/[0.02] px-3 py-2.5 text-center">
                  <p className="text-xl font-bold text-orange-500 sm:text-2xl">{s.value}</p>
                  <p className="mt-0.5 text-[10px] text-neutral-500 sm:text-[11px]">{s.label}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-2 justify-center lg:justify-start">
              {TECH_STACK.slice(0, 5).map((t) => (
                <div
                  key={t.name}
                  className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[10px] text-neutral-400 sm:px-3 sm:text-xs"
                >
                  <span className="h-1 w-1 rounded-full bg-orange-500/60 sm:h-1.5 sm:w-1.5" />
                  {t.name}
                </div>
              ))}
            </div>
          </div>

          {/* Right — CTA form */}
          <div className="w-full max-w-md shrink-0">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-sm sm:p-6">
              <h2 className="mb-1 text-base font-semibold text-white sm:text-lg">
                Start Investigation
              </h2>
              <p className="mb-4 text-xs text-neutral-500 sm:mb-5 sm:text-sm">
                Enter a target to investigate, or try the demo.
              </p>

              <div className="space-y-3.5 sm:space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-medium text-neutral-400 sm:text-xs">
                    Target Name
                  </label>
                  <Input
                    value={targetName}
                    onChange={(e) => setTargetName(e.target.value)}
                    placeholder="Enter person's name"
                    className="border-white/10 bg-white/5 text-white placeholder:text-neutral-600 h-10 sm:h-11"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] font-medium text-neutral-400 sm:text-xs">
                    Context
                  </label>
                  <Input
                    value={targetContext}
                    onChange={(e) => setTargetContext(e.target.value)}
                    placeholder="e.g., CEO of Company X"
                    className="border-white/10 bg-white/5 text-white placeholder:text-neutral-600 h-10 sm:h-11"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-[11px] font-medium text-neutral-400 sm:text-xs">
                      Max Search Iterations
                    </label>
                    <span className="font-mono text-xs text-orange-400 sm:text-sm">
                      {maxIterations}
                    </span>
                  </div>
                  <Slider
                    value={[maxIterations]}
                    onValueChange={([v]) => setMaxIterations(v)}
                    min={1}
                    max={10}
                    step={1}
                    className="py-2"
                  />
                </div>

                <div className="flex gap-3 pt-1">
                  <Button
                    onClick={handleStart}
                    disabled={!targetName.trim()}
                    className="flex-1 bg-orange-600 text-white hover:bg-orange-700 h-10 sm:h-11"
                    size="lg"
                  >
                    Investigate
                  </Button>
                  <Button
                    onClick={() => router.push("/investigate?demo=true")}
                    variant="outline"
                    className="border-orange-500/30 text-orange-400 hover:bg-orange-500/10 hover:text-orange-300 h-10 sm:h-11"
                    size="lg"
                  >
                    Demo
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FEATURES ─────────────────────────────────────────── */}
      <section className="border-t border-white/5 bg-neutral-950/50 py-12 sm:py-16 md:py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              Built for Serious Research
            </h2>
            <p className="mt-2 text-sm text-neutral-400 sm:mt-3 sm:text-base">
              Everything you need for autonomous due diligence investigation.
            </p>
          </div>

          <div className="mt-8 grid gap-4 sm:mt-12 sm:grid-cols-2 sm:gap-5 lg:mt-14 lg:grid-cols-3 lg:gap-6">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-xl border border-white/5 bg-white/[0.02] p-4 transition-colors hover:border-orange-500/20 hover:bg-orange-500/[0.03] sm:p-5 md:p-6"
              >
                <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-orange-500/10 text-orange-400 transition-colors group-hover:bg-orange-500/20 sm:mb-4 sm:h-10 sm:w-10">
                  {feature.icon}
                </div>
                <h3 className="mb-1.5 text-sm font-semibold text-white sm:mb-2">
                  {feature.title}
                </h3>
                <p className="text-xs leading-relaxed text-neutral-500 sm:text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────── */}
      <section className="border-t border-white/5 py-12 sm:py-16 md:py-20">
        <div className="mx-auto max-w-4xl px-4 sm:px-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              How It Works
            </h2>
            <p className="mt-2 text-sm text-neutral-400 sm:mt-3 sm:text-base">
              A 7-step autonomous pipeline powered by LangGraph. Steps 2-5
              loop adaptively until coverage is sufficient.
            </p>
          </div>

          <div className="mt-8 space-y-0 sm:mt-12 lg:mt-14">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.step} className="relative flex gap-4 sm:gap-6">
                {/* Vertical connector line */}
                {i < PIPELINE_STEPS.length - 1 && (
                  <div className="absolute left-[18px] top-12 bottom-0 w-px bg-gradient-to-b from-orange-500/30 to-white/5 sm:left-5 sm:top-14" />
                )}

                {/* Step number circle */}
                <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-orange-500/30 bg-orange-500/10 text-orange-400 sm:h-10 sm:w-10">
                  {step.icon}
                </div>

                {/* Content */}
                <div className="pb-8 sm:pb-10">
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                    <span className="font-mono text-[10px] text-orange-500/60 sm:text-xs">
                      STEP {step.step}
                    </span>
                    <span className="rounded-full bg-white/5 px-2 py-0.5 text-[9px] font-medium text-neutral-500 sm:text-[10px]">
                      {step.tech}
                    </span>
                  </div>
                  <h3 className="mt-1 text-base font-semibold text-white sm:text-lg">
                    {step.title}
                  </h3>
                  <p className="mt-1 text-xs leading-relaxed text-neutral-500 sm:mt-1.5 sm:text-sm">
                    {step.description}
                  </p>

                  {/* Loop indicator after step 5 */}
                  {step.step === "05" && (
                    <div className="mt-2.5 flex items-center gap-2 rounded-lg border border-orange-500/15 bg-orange-500/5 px-2.5 py-1.5 text-[10px] text-orange-400/80 sm:mt-3 sm:px-3 sm:py-2 sm:text-xs">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4">
                        <path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      Loops back to Step 02 if more investigation is needed
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── TECH STACK ───────────────────────────────────────── */}
      <section className="border-t border-white/5 bg-neutral-950/50 py-10 sm:py-14 md:py-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6">
          <h2 className="text-center text-xl font-bold text-white sm:text-2xl">
            Tech Stack
          </h2>
          <div className="mt-6 grid grid-cols-2 gap-3 sm:mt-8 sm:grid-cols-4 sm:gap-4 md:mt-10">
            {TECH_STACK.map((t) => (
              <div
                key={t.name}
                className="rounded-xl border border-white/5 bg-white/[0.02] p-3 text-center sm:p-4"
              >
                <p className="text-xs font-semibold text-white sm:text-sm">{t.name}</p>
                <p className="mt-0.5 text-[10px] text-neutral-500 sm:mt-1 sm:text-xs">{t.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────── */}
      <footer className="border-t border-white/5 py-6 sm:py-8">
        <div className="mx-auto max-w-6xl px-4 text-center sm:px-6">
          <p className="text-[10px] text-neutral-600 sm:text-xs">
            <span className="text-orange-500/60 font-semibold">masst spy</span> &middot; Built by Aditya Narayan
          </p>
        </div>
      </footer>
    </div>
  );
}
