# Design Approach & Architecture

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Step-by-Step Agent Flow](#step-by-step-agent-flow)
- [Multi-Model Strategy](#multi-model-strategy)
- [Consecutive Search Strategy](#consecutive-search-strategy)
- [Prompt Engineering](#prompt-engineering)
- [Identity Graph Design](#identity-graph-design)
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
│                          STREAMLIT FRONTEND (app.py)                            │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Input    │  │  Live Agent  │  │  Identity     │  │  Risk Assessment    │   │
│  │  Form     │  │  Progress    │  │  Graph (HTML) │  │  Report             │   │
│  └──────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────────────┘
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
│  │ (Gemini)    │    │ (NetworkX)   │    │ (Gemini)         │                   │
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
│ Identity     │    │ Risk Assessment  │    │ LangSmith        │
│ Graph (HTML) │    │ Report (MD)      │    │ Traces           │
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
**Tool**: Tavily API (advanced search depth)

Runs each query through Tavily and collects structured results:

```
For each query:
  → Tavily API call (max 5 results per query)
  → Returns: { url, title, content, relevance_score }
  → 1-second delay between queries (rate limiting)
  → Deduplicates by URL across all iterations
```

**Per iteration**: 5 queries × 5 results = ~25 new search results
**Across 3 iterations**: ~75 total results processed

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

### Technology Choice: NetworkX + pyvis
- **NetworkX**: Python graph library for construction and analysis
- **pyvis**: Converts NetworkX graphs to interactive HTML using vis.js
- **No external services needed** — no Docker, no cloud databases

### Visual Encoding

```
Node Shape + Color = Entity Type
  👤 Blue circle    = Person
  🏢 Orange diamond = Organization
  📅 Green triangle = Event
  📄 Purple square  = Filing
  📍 Red star       = Location
  🔴 Large red dot  = Investigation target (highlighted)

Edge Color = Confidence Level
  🟢 Green  = High confidence (≥80%)
  🟡 Yellow = Medium confidence (≥50%)
  🔴 Red    = Low confidence (<50%)

Edge Width = Proportional to confidence score
Edge Label = Relationship predicate (e.g., "is CEO of", "charged")
Edge Arrow = Direction of relationship
```

### Physics Layout
The graph uses ForceAtlas2 physics simulation for natural-looking layouts where:
- Connected nodes cluster together
- The target stays central
- Unrelated entities drift to the periphery

---

## Evaluation Framework

### Design Philosophy
The assignment explicitly states: *"Before starting, make sure to develop an evaluation set."*

We defined 3 personas with ground-truth facts **before building the agent**, then used them to measure performance.

### Persona 1: Timothy Overturf (Primary Target — Hard)
- **Challenge**: Limited online presence
- **Tests**: Agent's ability to find information on less-public individuals
- **Ground truth**: 1 verified fact, 2 known entities
- **Expected categories**: professional, financial

### Persona 2: Elizabeth Holmes (Baseline — Easy)
- **Challenge**: Extremely well-documented
- **Tests**: Basic search and extraction capabilities (should achieve >80% recall)
- **Ground truth**: 10 verified facts, 6 known entities
- **Expected categories**: professional, legal, financial, biographical, regulatory, social

### Persona 3: Martin Shkreli (Depth Test — Medium)
- **Challenge**: Complex network of companies, legal issues, controversies
- **Tests**: Ability to uncover non-obvious connections and trace corporate relationships
- **Ground truth**: 8 verified facts, 5 known entities
- **Expected categories**: professional, legal, financial, social

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

### Rate Limiting
- **Search**: 1-second delay between Tavily API calls (configurable)
- **LLM**: Gemini auto-retries with exponential backoff on 429 errors
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
| Graph DB | NetworkX + pyvis | Neo4j | Zero setup, no Docker. Interactive HTML output is more portable for demos. Neo4j would be better for production (persistent storage, Cypher queries). |
| Search API | Tavily | SerpAPI, Google Custom Search | Tavily is built for AI agents — returns clean, structured content. Free tier (1000 searches/month) is sufficient. |
| LLM for extraction | Groq/Llama 3.3 70B | GPT-4, Claude | Free, ~500 tok/sec (5-10x faster). Extraction is pattern-based; doesn't need frontier reasoning. |
| LLM for analysis | Gemini 2.0 Flash | Claude, GPT-4 | Free tier available. Strong cross-referencing ability. Automatic fallback to Groq if rate-limited. |
| State management | TypedDict + reducers | Pydantic model | LangGraph natively supports TypedDict. Custom reducers handle list deduplication elegantly. |
| Eval approach | Fuzzy term matching | Exact string match | Real-world extraction paraphrases facts. Fuzzy matching (≥50% term overlap) is more realistic. |
| Rate limiting | Sequential, 1 req/sec | Parallel async | Simpler, respects API limits, avoids 429 errors. Async would be better for production throughput. |
| Model fallback | Gemini → Groq | Retry with backoff | Faster resolution. Waiting for Gemini recovery can add minutes of latency. |

---

## Sample Run: Timothy Overturf

### Execution Summary

```
Target: Timothy Overturf, CEO of Sisu Capital
Iterations: 3
Duration: ~7 minutes

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
  → 42 total facts extracted
  → 24 total entities discovered
  → 15 risk flags identified
  → Identity graph: 51 nodes, 35 edges
  → Full risk assessment report generated
```

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

### Current Design (Optimized for Demo)
- Single-threaded search execution
- In-memory graph (NetworkX)
- File-based output (HTML, Markdown)
- Free-tier APIs

### Production Evolution

| Aspect | Current | Production |
|--------|---------|------------|
| Graph storage | NetworkX (in-memory) | Neo4j (persistent, queryable with Cypher) |
| Search execution | Sequential | Async with aiohttp (parallel queries) |
| Caching | None | Redis (cache search results, reduce API calls) |
| API layer | CLI / Streamlit | FastAPI microservice |
| Authentication | None | OAuth2 / API keys per tenant |
| Deployment | Local Python | Docker → Kubernetes |
| Monitoring | LangSmith + file logs | LangSmith + Prometheus + Grafana |
| Rate limiting | time.sleep() | Token bucket with Redis |
| Multi-tenancy | Single user | Queue-based with Celery workers |

### What I Would Add With More Time

1. **Persistent knowledge base** — store all investigations in Neo4j, query across cases
2. **Webhook notifications** — notify when investigation completes
3. **PDF report export** — professional formatted reports
4. **Batch investigation mode** — investigate multiple targets in parallel
5. **Custom search sources** — SEC EDGAR API, PACER court records, OpenCorporates
6. **Confidence calibration** — use evaluation metrics to tune confidence thresholds
7. **Human-in-the-loop** — allow analyst to steer the investigation mid-run
