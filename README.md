# AI Research Agent — Autonomous Due Diligence

An autonomous research agent that investigates individuals for due diligence and risk assessment. Given a person's name, it autonomously searches the web, extracts structured facts, identifies risks, maps entity connections in a graph database, and generates an interactive identity graph — all through an iterative search loop that builds on its own findings.

**Three interfaces**: CLI, Streamlit dashboard, and a polished Next.js frontend with React Flow identity graph.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH STATE MACHINE                        │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐                │
│  │ 1. Query │──▶│ 2. Search│──▶│ 3. Fact      │                │
│  │ Planner  │   │ Executor │   │ Extractor    │                │
│  │ (Groq)   │   │ (Tavily) │   │ (Groq)       │                │
│  └──────────┘   └──────────┘   └──────┬───────┘                │
│                                        │                        │
│  ┌──────────┐   ┌──────────┐   ┌──────▼───────┐                │
│  │ 7. Report│◀──│ 6. Graph │◀──│ 4. Risk      │                │
│  │ Generator│   │ Builder  │   │ Analyzer     │                │
│  │ (Gemini) │   │(NetworkX)│   │ (Gemini)     │                │
│  └──────────┘   └──────────┘   └──────┬───────┘                │
│                                        │                        │
│                                ┌───────▼───────┐               │
│                    ┌──────────▶│ 5. Query      │               │
│                    │  LOOP     │ Refiner (Groq)│               │
│                    │           └───┬───────┬───┘               │
│                    │           YES │       │ NO                 │
│                    └───────────────┘       ▼                    │
│                                      To Graph Builder           │
└──────────────────────────────────────────────────────────────────┘
```

**Key feature**: The agent loops through Steps 2-5 up to 5 times, discovering new entities each iteration and generating targeted follow-up queries. This is how it uncovers non-obvious connections.

## Features

- **Multi-Model AI**: Groq (Llama 3.3 70B) for fast extraction + Gemini 2.0 Flash for deep risk analysis
- **Consecutive Search Loop**: Iteratively discovers entities and refines queries (up to 5 iterations)
- **Graph Database**: NetworkX + SQLite backend with centrality, community detection, and shortest-path analytics
- **Interactive Identity Graph**: React Flow frontend with dagre layout, GSAP animations, and click-to-highlight
- **Risk Assessment**: 5-level severity scoring across regulatory, financial, legal, reputational, and inconsistency categories
- **Confidence Scoring**: Every fact has a 0-1.0 confidence score with source URLs
- **FastAPI + SSE Backend**: Real-time streaming of investigation progress to the Next.js frontend
- **Evaluation Framework**: 3 test personas with detailed ground-truth JSON files for benchmarking
- **LLM Retry with Backoff**: Exponential backoff retry wrapper for all LLM calls (configurable max retries + delays)
- **LangSmith Tracing**: Full observability of every LLM call, prompt, and response
- **Resilient**: Automatic model fallback (Gemini → Groq) on rate limits

## Quick Start

### 1. Clone and setup
```bash
git clone https://github.com/AdityaNarayan29/deriv-ai-research-agent.git
cd deriv-ai-research-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
```
Edit `.env` with your keys (all free tier):
| Key | Get it from |
|-----|-------------|
| `GROQ_API_KEY` | https://console.groq.com/keys |
| `GOOGLE_API_KEY` | https://aistudio.google.com/apikey |
| `TAVILY_API_KEY` | https://tavily.com |
| `LANGCHAIN_API_KEY` | https://smith.langchain.com |

### 3. Run via CLI
```bash
python main.py "Timothy Overturf" "CEO of Sisu Capital" 5
```

### 4. Run via Streamlit UI
```bash
streamlit run app.py
# → http://localhost:8501
```

### 5. Run the Next.js Frontend + FastAPI
```bash
# Terminal 1 — FastAPI backend (SSE streaming)
uvicorn api:app --port 8000 --reload

# Terminal 2 — Next.js frontend
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

The Next.js frontend connects to FastAPI on `:8000`, which streams SSE events as the agent runs. A demo mode is available that uses pre-built investigation data (45 facts, 26 entities, 8 risk flags) to showcase the full UI without API calls.

### 6. Run evaluation
```bash
# All 3 personas
python evaluation/run_eval.py

# Single persona (1=Timothy, 2=Elizabeth Holmes, 3=Martin Shkreli)
python evaluation/run_eval.py 2
```

## Sample Output (Timothy Overturf — Demo Data)

**45 facts** extracted | **26 entities** discovered | **8 risk flags** | **27-node identity graph** with **36 edges**

Key findings the agent uncovered autonomously:
- SEC charged Timothy Overturf and Sisu Capital with securities violations
- Unauthorized trades and breach of fiduciary duties
- Father (Hans Overturf) was a suspended investment adviser involved in client advice
- Sisu Capital invested client funds in thinly-traded bank stock (Redwood Capital Bancorp)
- Timothy founded the firm at age 18
- FINRA registrations and California DFPI regulatory actions

## Project Structure

```
├── APPROACH.md                 # Detailed design decisions and architecture
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── api.py                      # FastAPI backend — SSE streaming + demo mode
├── app.py                      # Streamlit UI
├── demo_data.py                # Pre-built Timothy Overturf investigation data
├── main.py                     # CLI entry point
├── config/
│   └── settings.py             # Centralized configuration
├── agent/
│   ├── state.py                # Pydantic data models + LangGraph AgentState
│   ├── graph.py                # LangGraph assembly + LangSmith wiring
│   ├── llm_retry.py            # Exponential backoff retry wrapper for LLM calls
│   ├── nodes/
│   │   ├── query_planner.py    # Generates search queries (Groq)
│   │   ├── search_executor.py  # Runs Tavily searches (parallel via ThreadPoolExecutor)
│   │   ├── fact_extractor.py   # Extracts structured facts (Groq)
│   │   ├── risk_analyzer.py    # Identifies risks (Gemini → Groq fallback)
│   │   ├── query_refiner.py    # Decides search continuation (Groq)
│   │   ├── graph_builder.py    # Builds identity graph (NetworkX + pyvis)
│   │   └── report_generator.py # Generates report (Gemini → Groq fallback)
│   ├── edges/
│   │   └── routing.py          # Conditional edge logic for search loop
│   ├── graph_db/
│   │   ├── __init__.py         # Factory: get_graph_db(backend="networkx")
│   │   ├── interface.py        # Abstract GraphDBInterface (swap to Neo4j later)
│   │   ├── networkx_backend.py # NetworkX + SQLite implementation
│   │   └── analytics.py        # Centrality, community detection, shortest path
│   └── prompts/
│       └── templates.py        # All 5 prompt templates
├── evaluation/
│   ├── eval_data.py            # 3 test personas — ground truth facts + entities
│   ├── evaluator.py            # Metrics: recall, coverage, depth
│   ├── run_eval.py             # Evaluation runner
│   ├── persona_1_timothy_overturf.json  # Detailed persona (16 entities, 14 facts, 7 risks)
│   ├── persona_2_elizabeth_holmes.json  # Detailed persona (15 entities, 12 facts, 6 risks)
│   └── persona_3_martin_shkreli.json   # Detailed persona (14 entities, 11 facts, 7 risks)
├── frontend/                   # Next.js + React Flow frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Landing page with pipeline visualization
│   │   │   ├── globals.css
│   │   │   └── investigate/
│   │   │       └── page.tsx        # Investigation + results page (5 tabs)
│   │   ├── components/
│   │   │   ├── PipelineProgress.tsx # Step-by-step pipeline indicator
│   │   │   ├── ExecutionLog.tsx     # Real-time log viewer
│   │   │   ├── MetricsCards.tsx     # Animated counters (facts, entities, risks)
│   │   │   ├── ReportTab.tsx        # Markdown report renderer
│   │   │   ├── FactsTab.tsx         # Sortable facts list with confidence dots
│   │   │   ├── RisksTab.tsx         # Severity-ranked risk cards
│   │   │   ├── EntitiesTab.tsx      # Entity grid with type badges
│   │   │   └── graph/
│   │   │       ├── IdentityGraph.tsx     # React Flow container + legend
│   │   │       ├── EntityNode.tsx        # Custom node with type-colored shapes
│   │   │       ├── TargetNode.tsx        # Highlighted target node with glow
│   │   │       ├── transformGraphData.ts # Entity/fact → nodes/edges (dagre layout)
│   │   │       └── useGraphAnimations.ts # GSAP staggered entrance animations
│   │   ├── hooks/
│   │   │   └── useInvestigation.ts  # useReducer SSE state machine
│   │   └── lib/
│   │       ├── types.ts             # TypeScript interfaces (mirrors state.py)
│   │       ├── api.ts               # SSE client for FastAPI
│   │       └── constants.ts         # Entity colors, confidence thresholds
│   ├── next.config.ts               # API proxy → localhost:8000
│   └── package.json
└── outputs/
    ├── graphs/                 # Generated identity graph HTML files
    ├── reports/                # Generated risk assessment reports
    └── logs/                   # Execution logs
```

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Agent Orchestration | LangGraph | Stateful graph with conditional looping |
| Monitoring | LangSmith | Auto-traces all LLM calls |
| Model 1 (extraction) | Groq (Llama 3.3 70B) | Free, fast (~500 tok/s), reliable JSON |
| Model 2 (analysis) | Gemini 2.0 Flash | Free tier, strong analytical reasoning |
| Web Search | Tavily API | Built for AI agents, structured output |
| Graph Database | NetworkX + SQLite | Persistent storage, analytics (centrality, communities) |
| Graph Visualization | React Flow + dagre | Interactive, animated identity graph in the browser |
| Backend API | FastAPI + SSE | Real-time streaming of investigation progress |
| Frontend | Next.js + Tailwind + shadcn/ui | Modern, mobile-responsive UI |
| Streamlit | Streamlit | Rapid prototyping, live progress display |
| LLM Resilience | Custom retry wrapper | Exponential backoff with configurable retries |

## Evaluation

3 test personas with ground-truth data, defined **before** building the agent:

| Persona | Ground Truth Facts | Ground Truth Entities | Expected Risks | Difficulty |
|---------|-------------------|----------------------|----------------|------------|
| Timothy Overturf | 14 | 16 | 7 | Hard — limited public info |
| Elizabeth Holmes | 12 | 15 | 6 | Easy — well-documented |
| Martin Shkreli | 11 | 14 | 7 | Medium — complex connections |

Each persona has a detailed JSON file (`evaluation/persona_*.json`) with scoring criteria, expected entity types, fact categories, and risk severities.

Metrics: Recall, Category Coverage, Depth Score. See [APPROACH.md](APPROACH.md) for details.

## Design Decisions

See [APPROACH.md](APPROACH.md) for:
- Multi-model strategy (why Groq for extraction, Gemini for analysis)
- Consecutive search design (how iterations build on each other)
- Prompt engineering approach (anti-hallucination guards, structured output)
- Graph database architecture (NetworkX + SQLite with abstract interface for Neo4j swap)
- FastAPI SSE streaming architecture
- Trade-offs table (what was chosen, what was considered, why)
- Production scalability roadmap
