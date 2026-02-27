# Design Approach & Architecture

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Step-by-Step Agent Flow](#step-by-step-agent-flow)
- [Multi-Model Strategy](#multi-model-strategy)
- [Consecutive Search Strategy](#consecutive-search-strategy)
- [Prompt Engineering](#prompt-engineering)
- [Identity Graph Design](#identity-graph-design)
- [Graph Database Architecture](#graph-database-architecture)
- [FastAPI SSE Backend](#fastapi-sse-backend)
- [Next.js Frontend](#nextjs-frontend)
- [Evaluation Framework](#evaluation-framework)
- [Error Handling & Resilience](#error-handling--resilience)
- [LangSmith Observability](#langsmith-observability)
- [Trade-offs & Decisions](#trade-offs--decisions)
- [Sample Run: Timothy Overturf](#sample-run-timothy-overturf)
- [Scalability & Production Considerations](#scalability--production-considerations)

---

## Overview

This is an autonomous research agent that conducts comprehensive due diligence investigations. Given a person's name and context (e.g., "Timothy Overturf, CEO of Sisu Capital"), it:

1. **Autonomously searches** the web using diverse, targeted queries
2. **Extracts structured facts** as subject-predicate-object triples with confidence scores
3. **Identifies risks** by cross-referencing facts and flagging inconsistencies
4. **Iteratively deepens** the investigation by following discovered leads
5. **Generates an identity graph** showing all connections visually
6. **Produces a risk assessment report** with evidence-backed findings

The agent is built as a **LangGraph state machine** with 7 specialized nodes and a conditional search loop, orchestrated by two distinct AI models.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTENDS                                          │
│                                                                                 │
│  ┌────────────────────────────────┐   ┌────────────────────────────────────┐   │
│  │  Streamlit (app.py) :8501      │   │  Next.js (frontend/) :3000         │   │
│  │  ┌────────┐ ┌──────┐ ┌──────┐ │   │  ┌────────┐ ┌──────┐ ┌──────────┐│   │
│  │  │ Input  │ │ Live │ │ HTML │ │   │  │ React  │ │ SSE  │ │ React    ││   │
│  │  │ Form   │ │ Logs │ │Graph │ │   │  │ Flow   │ │Stream│ │ Markdown ││   │
│  │  └────────┘ └──────┘ └──────┘ │   │  │ Graph  │ │ Logs │ │ Report   ││   │
│  └────────────┬───────────────────┘   │  └────────┘ └──────┘ └──────────┘│   │
│               │ (direct)              └────────────┬───────────────────────┘   │
│               │                                    │ (HTTP + SSE)              │
│               │                         ┌──────────▼──────────┐               │
│               │                         │  FastAPI (api.py)    │               │
│               │                         │  :8000               │               │
│               │                         └──────────┬──────────┘               │
│               └──────────────┬─────────────────────┘                          │
│                              ▼                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH STATE MACHINE (agent/graph.py)                 │
│                                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐                   │
│  │ 1. QUERY    │───▶│ 2. SEARCH    │───▶│ 3. FACT          │                   │
│  │ PLANNER     │    │ EXECUTOR     │    │ EXTRACTOR        │                   │
│  │ (Groq)      │    │ (Tavily API) │    │ (Groq/Llama 3.3) │                   │
│  └─────────────┘    └──────────────┘    └────────┬─────────┘                   │
│                                                   │                             │
│                                                   ▼                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐                   │
│  │ 7. REPORT   │◀───│ 6. GRAPH     │◀───│ 4. RISK          │                   │
│  │ GENERATOR   │    │ BUILDER      │    │ ANALYZER         │                   │
│  │ (Gemini)    │    │ (NetworkX+   │    │ (Gemini)         │                   │
│  │             │    │  SQLite)     │    │                  │                   │
│  └─────────────┘    └──────────────┘    └────────┬─────────┘                   │
│                                                   │                             │
│                                          ┌────────▼─────────┐                   │
│                                          │ 5. QUERY          │                   │
│                          ┌──────────────▶│ REFINER           │                   │
│                          │  LOOP         │ (Groq)            │                   │
│                          │               └────────┬─────────┘                   │
│                          │                        │                             │
│                          │    new entities found?  │                             │
│                          │    ┌─────┐    ┌─────┐  │                             │
│                          └────│ YES │    │ NO  │──┘                             │
│                               └─────┘    └──┬──┘                               │
│                             back to          go to                              │
│                             Node 2           Node 6                             │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Graph DB     │    │ Risk Assessment  │    │ LangSmith        │
│ (SQLite)     │    │ Report (MD)      │    │ Traces           │
└──────────────┘    └──────────────────┘    └──────────────────┘
```

---

## Step-by-Step Agent Flow

### Step 1: Query Planner → `agent/nodes/query_planner.py`
**Model**: Groq (Llama 3.3 70B) | **Temperature**: 0.3

Takes the target name and generates 5 diverse search queries covering different angles:

```
Input:  "Timothy Overturf", "CEO of Sisu Capital"

Output (Iteration 1):
  1. "Timothy Overturf Sisu Capital biography education background"
  2. "Timothy Overturf Sisu Capital career leadership"
  3. "Sisu Capital fund performance financials"
  4. "Timothy Overturf SEC filing lawsuit regulatory action"
  5. "Timothy Overturf interview podcast public statement"

Output (Iteration 2 — INFORMED by previous findings):
  1. "Hans Overturf investment adviser suspension disciplinary action"
  2. "Timothy Overturf Hans Overturf business relationship family ties"
  3. "Sisu Capital SEC charges lawsuit litigation"
  4. "Timothy Overturf Uniform Investment Adviser Law Examination"
```

**Key design choice**: On subsequent iterations, the planner receives ALL previously discovered facts and entities, plus a list of already-completed queries to avoid duplication. This is how the "consecutive search" builds on itself.

---

### Step 2: Search Executor → `agent/nodes/search_executor.py`
**Tool**: Tavily API (advanced search depth) | **Execution**: Parallel via `ThreadPoolExecutor`

Runs each query through Tavily in parallel and collects structured results:

```
For each query (executed concurrently):
  → Tavily API call (max 5 results per query)
  → Returns: { url, title, content, relevance_score }
  → Deduplicates by URL across all iterations
```

**Per iteration**: 5 queries × 5 results = ~25 new search results
**Across 3 iterations**: ~75 total results processed

**Why parallel?** Sequential execution added ~5 seconds per query. Using `ThreadPoolExecutor` runs all 5 queries concurrently, cutting per-iteration search time from ~25s to ~5s.

---

### Step 3: Fact Extractor → `agent/nodes/fact_extractor.py`
**Model**: Groq (Llama 3.3 70B) | **Temperature**: 0.1

Reads raw search results and extracts structured facts as **Subject → Predicate → Object** triples:

```json
{
  "facts": [
    {
      "subject": "Timothy Overturf",
      "predicate": "is CEO of",
      "object": "Sisu Capital",
      "confidence": 0.95,
      "category": "professional"
    },
    {
      "subject": "SEC",
      "predicate": "charged",
      "object": "Timothy Overturf with securities violations",
      "confidence": 0.90,
      "category": "regulatory"
    }
  ],
  "new_entities": [
    {
      "name": "Hans Overturf",
      "type": "person",
      "description": "Father, suspended investment adviser"
    }
  ]
}
```

**6 fact categories**: biographical, professional, financial, legal, social, regulatory

**Why triples?** Subject-predicate-object is the standard representation for knowledge graphs. Each fact directly maps to a node and edge in the identity graph.

**Why Groq?** Extraction is structurally simple (pattern matching + JSON output) but must process large volumes of text. Groq's ~500 tokens/sec speed makes it 5-10x faster than alternatives for this task.

---

### Step 4: Risk Analyzer → `agent/nodes/risk_analyzer.py`
**Model**: Gemini 2.0 Flash (primary) → Groq (fallback) | **Temperature**: 0.2

Cross-references ALL accumulated facts and identifies:

```
From Timothy Overturf investigation:

[5/5 CRITICAL - regulatory]   SEC violations and regulatory non-compliance
[5/5 CRITICAL - financial]    Unauthorized trades, breach of fiduciary duties
[5/5 CRITICAL - reputational] Lawsuits and negative press from SEC charges
[4/5 HIGH     - financial]    Conflict of interest — father Hans Overturf
                               (suspended adviser) involved in client advice
[3/5 MODERATE - inconsistency] Inconsistent biography, started firm at age 18
```

**Why Gemini for this?** Risk analysis requires connecting dots across many unrelated facts — "this person was suspended AND his son runs a fund AND the SEC charged both of them." This is reasoning-heavy work where model quality matters more than speed.

**Fallback**: If Gemini hits rate limits (429), automatically falls back to Groq/Llama without losing any data or crashing.

---

### Step 5: Query Refiner → `agent/nodes/query_refiner.py` — THE DECISION POINT
**Model**: Groq (Llama 3.3 70B) | **Temperature**: 0.2

This is the control hub of the search loop. It examines the current state and makes a binary decision: **keep searching or stop?**

```
Decision inputs:
  - Uninvestigated entities (discovered but not yet searched)
  - Low-confidence facts (need verification)
  - Risk flags (do any need more evidence?)
  - Iteration count vs. max allowed

Decision logic:
  IF new high-priority entities AND iteration < max → CONTINUE
  IF critical risk flags need verification → CONTINUE
  IF max iterations reached OR diminishing returns → STOP
```

**From the actual Timothy Overturf run**:
- **Iteration 1 → CONTINUE**: "Hans Overturf uninvestigated, SEC charges need verification"
- **Iteration 2 → CONTINUE**: "State of California involvement needs investigation"
- **Iteration 3 → STOP**: "Max iterations reached, diminishing returns, risk flags well-documented"

---

### Step 6: Graph Builder → `agent/nodes/graph_builder.py`
**Tool**: NetworkX + pyvis

Takes ALL entities and facts and builds a directed identity graph:

```
Node types (color-coded):
  - Person:       Blue circle       (Timothy Overturf, Hans Overturf)
  - Organization: Orange diamond    (Sisu Capital, SEC, FINRA)
  - Event:        Green triangle    (SEC complaint, lawsuits)
  - Filing:       Purple square     (regulatory filings)
  - Location:     Red star          (Mill Valley, California)

Edge properties:
  - Label:     relationship predicate ("is CEO of", "charged", "suspended")
  - Color:     Green (≥80% confidence), Yellow (≥50%), Red (<50%)
  - Width:     proportional to confidence score
  - Direction: arrows show relationship direction

Target node: Highlighted in red, larger, centered
```

**Output**: Interactive HTML file — you can zoom, pan, hover over nodes for details, drag nodes to rearrange.

**From Timothy Overturf run**: 51 nodes, 35 edges

---

### Step 7: Report Generator → `agent/nodes/report_generator.py`
**Model**: Gemini 2.0 Flash (primary) → Groq (fallback) | **Temperature**: 0.3

Generates a structured markdown report with 7 sections:

1. **Executive Summary** — Key findings and overall risk level
2. **Subject Profile** — Verified biographical and professional details
3. **Organizational Connections** — Mapped relationships and their significance
4. **Risk Assessment** — Each risk flag ranked by severity with evidence citations
5. **Key Findings** — Non-obvious discoveries and patterns
6. **Confidence Assessment** — Coverage gaps and reliability of findings
7. **Recommendations** — Actionable next steps

**Every claim in the report cites specific fact IDs** so findings are traceable back to source evidence.

---

## Multi-Model Strategy

### Why Two Different Models?

| Task | Model | Why This Model |
|------|-------|----------------|
| Query Planning | Groq/Llama 3.3 70B | Fast query generation, good structured output |
| Search Execution | Tavily API | Not an LLM — web search tool |
| Fact Extraction | Groq/Llama 3.3 70B | Speed-critical (processes 25+ results per iteration), reliable JSON |
| Risk Analysis | Gemini 2.0 Flash | Analytical reasoning, cross-referencing across many facts |
| Query Refinement | Groq/Llama 3.3 70B | Fast decision-making, simple structured output |
| Graph Building | NetworkX | Not an LLM — graph library |
| Report Generation | Gemini 2.0 Flash | Long-form analytical writing, citation-aware |

### The Reasoning

**Groq/Llama** is used where **speed matters more than depth**:
- Query planning: generate 5 queries quickly
- Fact extraction: process 25 search results per iteration
- Query refinement: make a quick continue/stop decision

**Gemini** is used where **reasoning depth matters more than speed**:
- Risk analysis: "Person A was suspended → his son runs a fund → SEC charged both" — connecting these dots requires strong reasoning
- Report generation: producing a coherent, well-structured analytical report

### Resilience: Automatic Fallback

Both Gemini-powered nodes have **automatic Groq fallback**:
```
Risk Analyzer:    Gemini → (if 429 rate limit) → Groq
Report Generator: Gemini → (if 429 rate limit) → Groq
```
The agent never crashes from API failures — it degrades gracefully.

---

## Consecutive Search Strategy

This is the core differentiator of the agent. Instead of a single flat search, it **builds knowledge iteratively**:

```
Iteration 1: Broad search
  Queries: "Timothy Overturf Sisu Capital", "Sisu Capital SEC filings"
  Discovered: Hans Overturf (father), SEC complaints, FINRA

Iteration 2: Targeted follow-up (informed by Iteration 1)
  Queries: "Hans Overturf investment adviser suspension",
           "Sisu Capital SEC charges Timothy Overturf"
  Discovered: State of California involvement, law firms, more details

Iteration 3: Deep verification (informed by Iterations 1+2)
  Queries: "Hans Overturf disciplinary action State of California",
           "Sisu Capital SEC charges Hansueli Overturf"
  Result: Verified risk flags, confirmed connections, reached saturation
```

**How it works technically**:
1. The `AgentState` accumulates facts and entities across iterations
2. The Query Planner receives `previous_findings` (all facts + entities found so far)
3. The Query Planner also receives `completed_queries` to avoid duplicates
4. The Query Refiner examines `uninvestigated_entities` — entities discovered but not yet searched
5. The conditional edge routes back to Search Executor if more searching is needed

This mimics how a human OSINT analyst works: start broad, follow leads, go deep on connections.

---

## Prompt Engineering

Each node has a carefully designed prompt in `agent/prompts/templates.py`. Key design principles:

### 1. Structured Output
Every prompt requests **exact JSON format** with field names and types specified:
```
Respond in this exact JSON format:
{
  "facts": [
    {
      "subject": "entity name",
      "predicate": "relationship",
      "object": "other entity or value",
      "confidence": 0.8,
      "category": "professional"
    }
  ]
}
```

### 2. Category-Aware Extraction
The Fact Extractor prompt explicitly lists 6 categories to ensure comprehensive coverage:
- Biographical, Professional, Financial, Legal, Social, Regulatory

### 3. Evidence-Grounded Analysis
The Risk Analyzer prompt requires **evidence citations** for every risk flag:
```
"Don't flag things as risks without evidence — speculation is not a risk flag"
```

### 4. Anti-Hallucination Guards
Multiple prompts include explicit guardrails:
```
"Do NOT fabricate or infer facts beyond what the text states"
"Only extract facts supported by the search results"
"Be precise with names, dates, and amounts"
```

### 5. Context-Aware Refinement
The Query Refiner prompt receives the full investigation context to make informed decisions:
```
- Uninvestigated entities
- Current risk flags
- Low-confidence facts needing verification
- All completed queries
```

---

## Identity Graph Design

### Technology: NetworkX + pyvis (Streamlit) / React Flow + dagre (Next.js)

Two visualization paths, same underlying data:

1. **Streamlit path**: NetworkX builds the graph → pyvis renders interactive HTML using vis.js
2. **Next.js path**: Facts + entities sent via SSE → `transformGraphData.ts` builds React Flow nodes/edges → dagre computes hierarchical layout → GSAP animates entrance

### Visual Encoding

```
Node Shape + Color = Entity Type
  Person:       Blue (#6366f1)    = circle
  Organization: Orange (#f59e0b)  = diamond
  Event:        Green (#10b981)   = triangle
  Filing:       Purple (#8b5cf6)  = square
  Location:     Red (#ef4444)     = star
  Target:       Large red node with gold border = highlighted center

Edge Color = Confidence Level
  Green (#10b981)  = High confidence (≥80%)
  Yellow (#eab308) = Medium confidence (≥50%)
  Red (#ef4444)    = Low confidence (<50%)

Edge Width = Proportional to confidence score
Edge Label = Relationship predicate (e.g., "is CEO of", "charged")
Edge Arrow = Direction of relationship
```

### Layout Strategies
- **Streamlit (pyvis)**: ForceAtlas2 physics simulation — connected nodes cluster naturally
- **Next.js (dagre)**: Hierarchical top-down layout — target at top center, entities spread below with 100px node separation and 130px rank separation

### Interactive Features (Next.js)
- **Click a node**: dims non-connected nodes/edges to 15% opacity, highlights direct connections
- **Click background**: resets all highlights
- **GSAP animations**: staggered fade-in of nodes on initial render
- **MiniMap**: overview panel for navigation (hidden on mobile)
- **Legend overlay**: color-coded entity type reference

---

## Graph Database Architecture

### Why a Graph DB?
Due diligence investigations naturally form graphs — people connected to organizations connected to regulatory actions. Storing this in a graph database enables:
- **Centrality analysis**: Which entity is the most connected? (degree centrality, betweenness centrality)
- **Community detection**: Which entities cluster together?
- **Shortest path**: How is Entity A connected to Entity B?
- **Persistence**: SQLite stores the graph between sessions

### Architecture: Abstract Interface + Swappable Backend

```
agent/graph_db/
├── interface.py        # Abstract GraphDBInterface
├── networkx_backend.py # NetworkX + SQLite implementation
├── analytics.py        # Centrality, community detection, shortest path
└── __init__.py         # Factory: get_graph_db(backend="networkx")
```

**`GraphDBInterface`** defines the contract:
- `add_entity()`, `add_relationship()`, `get_entity()`, `get_neighbors()`
- `shortest_path()`, `connected_components()`
- `degree_centrality()`, `betweenness_centrality()`, `community_detection()`
- `save()`, `load()`, `clear()`

**`NetworkXBackend`** implements this using NetworkX for in-memory graph operations and SQLite for persistence. The abstract interface means swapping to Neo4j requires only a new backend class — no changes to calling code.

### SQLite Schema
- `entities` table: id, name, type, description, metadata JSON
- `relationships` table: source_id, target_id, type, weight, metadata JSON
- Graph loaded into NetworkX on startup for fast analytics, saved back to SQLite on mutation

---

## FastAPI SSE Backend

### Why FastAPI + SSE?
The LangGraph agent takes 3-7 minutes to run. Users need real-time progress feedback, not a loading spinner. Server-Sent Events (SSE) provide a simple, unidirectional stream over HTTP.

### Architecture (`api.py`)

```
POST /api/investigate → Start investigation, returns SSE stream
POST /api/demo        → Start demo investigation (pre-built data, no API keys needed)
GET  /api/health      → API key status check
```

### SSE Event Types
```
node_start       → { node: "query_planner", iteration: 0 }
log              → { message: "Generated 5 queries" }
facts_update     → { facts: [...], total: 18 }
entities_update  → { entities: [...], total: 11 }
risks_update     → { risks: [...], total: 5 }
complete         → { report: "...", facts: [...], entities: [...], risks: [...] }
error            → { message: "API rate limit exceeded" }
```

### Demo Mode
`demo_data.py` contains a pre-built Timothy Overturf investigation with 45 facts, 26 entities, 8 risk flags, and a complete markdown report. The demo endpoint distributes this data across 3 simulated iterations with realistic timing delays — no API keys required. This allows showcasing the full UI without consuming API quota.

---

## Next.js Frontend

### Why a Second Frontend?
Streamlit is excellent for rapid prototyping, but limited for complex interactive visualizations. The Next.js frontend provides:
- **React Flow identity graph** with dagre layout, hover interactions, and GSAP animations
- **Real-time SSE streaming** of investigation progress
- **Mobile-responsive design** (tested down to 320px width)
- **Polished UI** with shadcn/ui components, dark theme, and smooth transitions

### Tech Stack
- **Next.js 15** + App Router + TypeScript
- **Tailwind CSS** + **shadcn/ui** for components
- **React Flow** (@xyflow/react) for the identity graph
- **dagre** for automatic hierarchical graph layout
- **GSAP** for entrance animations
- **react-markdown** + remark-gfm for report rendering

### State Management
`useInvestigation.ts` — a `useReducer`-based hook that acts as an SSE state machine:
```
idle → running → complete | error
```
Tracks: currentNode, progress, logs[], facts[], entities[], riskFlags[], report, iteration. Each SSE event dispatches to the reducer, which appends to lists and deduplicates by ID.

### Key Components
| Component | Purpose |
|-----------|---------|
| `PipelineProgress` | Horizontal 7-step indicator, current node pulses |
| `ExecutionLog` | Monospace scrolling log with auto-scroll |
| `MetricsCards` | Animated counter cards (facts, entities, risks, iterations) |
| `IdentityGraph` | React Flow container with legend, stats, MiniMap |
| `ReportTab` | Dark-themed markdown rendering with custom components |
| `FactsTab` | Sortable facts list with confidence dots and source links |
| `RisksTab` | Severity-ranked risk cards (5→1) with recommendations |
| `EntitiesTab` | Grid of entity cards with type badges |

### Mobile Responsiveness
Every component uses Tailwind responsive breakpoints (`sm:`, `md:`, `lg:`) to scale from mobile (320px) to desktop. Key adaptations:
- Graph height scales: 350px → 500px → 600px → 650px
- Legend and MiniMap hidden on mobile (< 640px)
- Tabs horizontally scrollable on narrow screens
- Text and padding scale proportionally

---

## Evaluation Framework

### Design Philosophy
The assignment explicitly states: *"Before starting, make sure to develop an evaluation set."*

We defined 3 personas with ground-truth facts **before building the agent**, then used them to measure performance.

### Persona 1: Timothy Overturf (Primary Target — Hard)
- **Challenge**: Limited online presence, niche financial industry figure
- **Tests**: Agent's ability to find information on less-public individuals
- **Ground truth**: 14 expected facts, 16 expected entities, 7 expected risks
- **Expected categories**: professional, financial, regulatory, legal
- **Detailed spec**: `evaluation/persona_1_timothy_overturf.json`

### Persona 2: Elizabeth Holmes (Baseline — Easy)
- **Challenge**: Extremely well-documented
- **Tests**: Basic search and extraction capabilities (should achieve >80% recall)
- **Ground truth**: 12 expected facts, 15 expected entities, 6 expected risks
- **Expected categories**: professional, legal, financial, biographical, regulatory, social
- **Detailed spec**: `evaluation/persona_2_elizabeth_holmes.json`

### Persona 3: Martin Shkreli (Depth Test — Medium)
- **Challenge**: Complex network of companies, legal issues, controversies
- **Tests**: Ability to uncover non-obvious connections and trace corporate relationships
- **Ground truth**: 11 expected facts, 14 expected entities, 7 expected risks
- **Expected categories**: professional, legal, financial, social
- **Detailed spec**: `evaluation/persona_3_martin_shkreli.json`

### Evaluation Data Structure
Each persona has two data sources:
1. **`eval_data.py`** — lightweight ground truth used by `run_eval.py` (fact strings + entity names)
2. **`persona_*.json`** — detailed scoring criteria with expected entity types, fact categories, risk severities, and scoring rubrics for manual review

### Metrics

| Metric | What It Measures | How It's Computed |
|--------|-----------------|-------------------|
| **Recall** | How many known facts did the agent find? | matched_facts / total_ground_truth |
| **Category Coverage** | Did it cover all expected fact categories? | found_categories ∩ expected / expected |
| **Depth Score** | Did it find non-obvious connections? | non_primary_entities / total_entities |

### Fuzzy Matching
Ground truth comparison uses **normalized term matching** rather than exact string comparison:
- Extract key terms (remove stop words)
- Match if ≥50% of ground truth terms appear in candidate fact
- This accounts for paraphrasing (e.g., "founded Theranos" ≈ "was the founder of Theranos")

---

## Error Handling & Resilience

### Every Node Has Try/Except

```
Query Planner:    Falls back to 3 basic hardcoded queries
Search Executor:  Marks failed queries as "completed" (prevents infinite retry)
Fact Extractor:   Logs error, returns empty (no facts lost)
Risk Analyzer:    Gemini → Groq fallback → returns empty
Query Refiner:    On error, sets should_continue=False (stops loop safely)
Graph Builder:    Returns empty if no data
Report Generator: Gemini → Groq fallback → raw data fallback (no LLM)
```

### LLM Retry with Exponential Backoff (`agent/llm_retry.py`)
All LLM calls are wrapped in a configurable retry decorator:
```
Attempt 1: call LLM
Attempt 2: wait 2s, retry
Attempt 3: wait 4s, retry
Attempt 4: wait 8s, retry (max)
```
- **Max retries**: 3 (configurable)
- **Base delay**: 2 seconds (doubles each attempt)
- **Max delay**: capped at 30 seconds
- Catches rate limit errors (429), transient network failures, and API timeouts
- Falls through to node-level error handling if all retries exhausted

### Rate Limiting
- **Search**: Parallel via `ThreadPoolExecutor` (5 queries concurrent)
- **LLM**: Exponential backoff retry on rate limit (429) errors
- **Model fallback**: If Gemini exhausts retries, falls back to Groq
- **All configurable** via `config/settings.py`

### Deduplication
- **URLs**: Search results deduplicated by URL across all iterations
- **Entities**: Deduplicated by name (case-insensitive) across iterations
- **Facts**: Deduplicated by UUID
- **Queries**: Completed queries tracked to prevent re-execution

---

## LangSmith Observability

### Setup
When `agent/graph.py` loads, it automatically sets the LangSmith environment variables:
```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = "deriv-research-agent"
```

### What Gets Traced
Every LangChain LLM call is automatically traced:
- **Input prompt** (full text sent to model)
- **Output response** (full model response)
- **Model used** (llama-3.3-70b-versatile, gemini-2.0-flash)
- **Token count** (input + output)
- **Latency** (milliseconds)
- **Status** (success/error)

### Custom Execution Logs
In addition to LangSmith, every node writes timestamped logs to the `execution_log` state field:
```
[2026-02-25T22:37:46] QueryPlanner: Generated 5 queries (iteration 0)
[2026-02-25T22:38:05] FactExtractor: Extracted 18 facts, 11 new entities
[2026-02-25T22:38:42] RiskAnalyzer (groq-fallback): Identified 5 risk flags
[2026-02-25T22:38:43] QueryRefiner: CONTINUE — Hans Overturf uninvestigated
[2026-02-25T22:44:42] GraphBuilder: Built graph with 51 nodes, 35 edges
[2026-02-25T22:45:19] ReportGenerator (groq-fallback): Generated report (4225 chars)
```

---

## Trade-offs & Decisions

| Decision | Chosen | Alternative | Why |
|----------|--------|-------------|-----|
| Graph DB | NetworkX + SQLite | Neo4j | Zero setup, no Docker. SQLite provides persistence. Abstract interface (`GraphDBInterface`) allows swapping to Neo4j with zero calling-code changes. |
| Graph Visualization | React Flow + dagre (Next.js) + pyvis (Streamlit) | D3.js, vis.js only | React Flow integrates natively with React. dagre gives deterministic hierarchical layouts. pyvis kept for Streamlit's HTML embedding. |
| Search API | Tavily | SerpAPI, Google Custom Search | Tavily is built for AI agents — returns clean, structured content. Free tier (1000 searches/month) is sufficient. |
| Search execution | Parallel (ThreadPoolExecutor) | Sequential, 1 req/sec | 5x faster per iteration. Tavily handles concurrent requests well. |
| LLM for extraction | Groq/Llama 3.3 70B | GPT-4, Claude | Free, ~500 tok/sec (5-10x faster). Extraction is pattern-based; doesn't need frontier reasoning. |
| LLM for analysis | Gemini 2.0 Flash | Claude, GPT-4 | Free tier available. Strong cross-referencing ability. Automatic fallback to Groq if rate-limited. |
| LLM resilience | Retry with backoff + model fallback | Single attempt | Retry catches transient 429 errors. If retries exhaust, Gemini → Groq fallback ensures the pipeline never blocks. |
| API layer | FastAPI + SSE | WebSockets, polling | SSE is simpler than WebSockets for unidirectional streaming. Native browser support, no library needed client-side. |
| Frontend | Next.js + shadcn/ui | Streamlit only | Streamlit kept for rapid iteration. Next.js added for polished, mobile-responsive UI with interactive graph. |
| State management | TypedDict + reducers | Pydantic model | LangGraph natively supports TypedDict. Custom reducers handle list deduplication elegantly. |
| Eval approach | Fuzzy term matching + JSON persona files | Exact string match | Real-world extraction paraphrases facts. Fuzzy matching (≥50% term overlap) is more realistic. JSON files add scoring rubrics. |

---

## Sample Run: Timothy Overturf

### Execution Summary

```
Target: Timothy Overturf, CEO of Sisu Capital
Iterations: 3
Duration: ~7 minutes (live) / ~15 seconds (demo mode)

Iteration 1:
  → 5 queries, 25 search results
  → 18 facts extracted, 11 new entities
  → 5 risk flags identified
  → Decision: CONTINUE (Hans Overturf uninvestigated)

Iteration 2:
  → 4 queries about Hans Overturf, SEC, FINRA
  → 20 search results, 13 new facts, 5 new entities
  → 5 additional risk flags
  → Decision: CONTINUE (verify SEC charges)

Iteration 3:
  → 4 queries verifying SEC complaints, State of California
  → 20 search results, 11 new facts, 8 new entities
  → 5 additional risk flags
  → Decision: STOP (max iterations, diminishing returns)

Final Output:
  → 45 total facts extracted (demo data)
  → 26 total entities discovered
  → 8 risk flags identified
  → Identity graph: 27 nodes, 36 edges
  → Full risk assessment report generated
```

### Demo Data
`demo_data.py` contains a curated version of this investigation with 45 facts designed so that every fact produces at least one edge in the identity graph (all subjects and objects match known entity names). This gives the graph maximum density for visual impact. The demo includes:
- 45 facts across all 6 categories (biographical, professional, financial, legal, social, regulatory)
- 26 entities across all 5 types (person, organization, event, filing, location)
- 8 risk flags from severity 2 (moderate) to 5 (critical)
- A complete markdown risk assessment report

### Key Findings Discovered

1. Timothy Overturf founded Sisu Capital at age 18 in 2013
2. SEC filed charges against Timothy Overturf and Sisu Capital
3. Allegations include unauthorized trades and breach of fiduciary duties
4. Hansueli (Hans) Overturf — father — was a suspended investment adviser
5. Hans Overturf was involved in providing advice to Sisu Capital clients despite suspension
6. Sisu Capital invested client funds in thinly-traded bank stock
7. FINRA suspended Hans Overturf
8. State of California took disciplinary action

---

## Scalability & Production Considerations

### Current Design
- Parallel search execution via `ThreadPoolExecutor`
- NetworkX + SQLite graph database (persistent, with analytics)
- FastAPI SSE backend for real-time streaming
- Next.js frontend with React Flow identity graph
- LLM retry with exponential backoff
- Free-tier APIs (Groq, Gemini, Tavily)

### Production Evolution

| Aspect | Current | Production |
|--------|---------|------------|
| Graph storage | NetworkX + SQLite | Neo4j (Cypher queries, native graph algorithms) |
| Search execution | Parallel (ThreadPoolExecutor) | Async with aiohttp (even higher concurrency) |
| Caching | None | Redis (cache search results, reduce API calls) |
| API layer | FastAPI + SSE | FastAPI + WebSockets (bidirectional) |
| Authentication | None | OAuth2 / API keys per tenant |
| Deployment | Local Python + Next.js | Docker → Kubernetes |
| Monitoring | LangSmith + file logs | LangSmith + Prometheus + Grafana |
| Rate limiting | Exponential backoff | Token bucket with Redis |
| Multi-tenancy | Single user | Queue-based with Celery workers |

### What I Would Add With More Time

1. **Persistent knowledge base** — store all investigations in Neo4j, query across cases
2. **Webhook notifications** — notify when investigation completes
3. **PDF report export** — professional formatted reports
4. **Batch investigation mode** — investigate multiple targets in parallel
5. **Custom search sources** — SEC EDGAR API, PACER court records, OpenCorporates
6. **Confidence calibration** — use evaluation metrics to tune confidence thresholds
7. **Human-in-the-loop** — allow analyst to steer the investigation mid-run
