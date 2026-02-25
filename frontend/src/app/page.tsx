"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";

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
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-lg border-white/10 bg-white/5 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/20 text-3xl">
            🔍
          </div>
          <CardTitle className="text-2xl font-bold text-white">
            AI Research Agent
          </CardTitle>
          <p className="text-sm text-slate-400">
            Autonomous due diligence investigation powered by LangGraph + Groq +
            Gemini
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">
              Target Name
            </label>
            <Input
              value={targetName}
              onChange={(e) => setTargetName(e.target.value)}
              placeholder="Enter person's name"
              className="border-white/10 bg-white/5 text-white placeholder:text-slate-500"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">
              Context
            </label>
            <Input
              value={targetContext}
              onChange={(e) => setTargetContext(e.target.value)}
              placeholder="e.g., CEO of Company X"
              className="border-white/10 bg-white/5 text-white placeholder:text-slate-500"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">
                Max Search Iterations
              </label>
              <span className="font-mono text-sm text-indigo-400">
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

          <Button
            onClick={handleStart}
            disabled={!targetName.trim()}
            className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
            size="lg"
          >
            Start Investigation
          </Button>

          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {["LangGraph", "Groq", "Gemini", "Tavily", "React Flow"].map(
              (tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-400"
                >
                  {tag}
                </span>
              )
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
