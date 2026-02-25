# Design Approach & Architecture

## Overview

This document explains the design decisions, trade-offs, and architecture of the autonomous research agent built for due diligence investigations.

## Architecture

The agent is built as a **directed graph** using LangGraph, with 7 specialized nodes connected by conditional edges. The core innovation is the **consecutive search loop** — the agent iteratively discovers new entities, refines its queries, and digs deeper until it reaches a configurable depth limit or diminishing returns.

```
START → Query Planner → Search Executor → Fact Extractor
     → Risk Analyzer → Query Refiner → [CONDITIONAL]
         ├─ Continue → Search Executor (loop)
         └─ Stop → Graph Builder → Report Generator → END
```

## Multi-Model Strategy

We use two models with **deliberate role assignment** based on their strengths:

### Model 1: Groq (Llama 3.3 70B) — Extraction & Planning
- **Used in**: Query Planner, Fact Extractor, Query Refiner
- **Why**: Groq's inference speed (~500 tokens/sec) makes it ideal for tasks requiring multiple fast iterations. Fact extraction is structurally simple but must process large volumes of text quickly. The Llama 3.3 70B model handles structured JSON output reliably.
- **Temperature**: 0.1-0.3 (low for consistency)

### Model 2: Google Gemini 2.5 Flash — Analysis & Reasoning
- **Used in**: Risk Analyzer, Report Generator
- **Why**: Gemini excels at analytical reasoning tasks requiring cross-referencing, pattern recognition, and nuanced assessment. Risk analysis requires connecting disparate facts and identifying subtle inconsistencies — tasks where reasoning depth matters more than speed.
- **Temperature**: 0.2-0.3 (slightly higher for creative risk identification)

### Why not use the same model for everything?
- Using specialized models for specific tasks reduces cost and latency
- Different tasks have different requirements: extraction needs speed, analysis needs depth
- This demonstrates understanding of model selection trade-offs (a key production consideration)

## Consecutive Search Strategy

The agent doesn't just search once — it builds on findings iteratively:

1. **Initial search**: broad queries about the target
2. **Entity discovery**: new people, companies, events are extracted
3. **Query refinement**: new queries target discovered entities
4. **Loop**: search → extract → analyze → refine → search again
5. **Termination**: when max depth reached OR no new entities found OR diminishing returns

This approach simulates how a human analyst works: start broad, follow leads, go deep on connections.

## Evaluation Framework

We built 3 test personas **before** building the agent (as specified in the assignment):

1. **Timothy Overturf** — primary target, limited online presence, tests edge-case handling
2. **Elizabeth Holmes** — well-documented, easy baseline, tests basic recall
3. **Martin Shkreli** — complex network, tests depth and connection mapping

### Metrics:
- **Recall**: How many known facts did the agent find?
- **Category Coverage**: Did it cover all expected fact categories?
- **Depth Score**: Ratio of non-obvious entities to total entities found
- **Fuzzy Matching**: Ground truth comparison uses normalized term matching

## Identity Graph Design

- **NetworkX** for graph construction (pure Python, no external dependencies)
- **pyvis** for interactive HTML visualization
- **Node types**: Person (blue), Organization (orange), Event (green), Filing (purple), Location (red)
- **Edge colors**: Green (high confidence), Yellow (medium), Red (low)
- **Edge width**: proportional to confidence score

## Trade-offs & Decisions

| Decision | Chosen | Alternative | Reasoning |
|----------|--------|-------------|-----------|
| Graph DB | NetworkX + pyvis | Neo4j | Zero setup, no Docker needed, interactive HTML output |
| Search API | Tavily | SerpAPI, Google | Built for AI agents, structured output, free tier |
| LLM for extraction | Groq/Llama | GPT-4, Claude | Free, extremely fast, reliable JSON output |
| LLM for analysis | Gemini Flash | Claude, GPT-4 | Free tier, strong reasoning, good at cross-referencing |
| Eval approach | Fuzzy matching | Exact match | Real-world extraction rarely matches verbatim |
| Rate limiting | 1 req/sec | Parallel | Respects API limits, prevents rate limiting errors |

## Production Considerations

- **Rate limiting**: configurable per-query delay to respect API limits
- **Error handling**: every node has try/except with fallback behavior
- **Deduplication**: URLs and entities are deduplicated to avoid redundant work
- **Configurable**: all parameters (iterations, thresholds, models) in settings.py
- **Tracing**: LangSmith integration for full observability of every step
- **Logging**: structured logging with timestamps for debugging

## Scalability

For production deployment, I would:
1. Replace NetworkX with Neo4j for persistent graph storage
2. Add Redis caching for search results
3. Implement parallel search execution with async I/O
4. Add user authentication and multi-tenant support
5. Deploy as a microservice with FastAPI
6. Add webhook notifications for completed investigations
