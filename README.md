# AI Research Agent — Autonomous Due Diligence

An autonomous research agent that investigates individuals for due diligence and risk assessment. Given a person's name, it autonomously searches the web, extracts structured facts, identifies risks, maps entity connections, and generates an interactive identity graph — all through an iterative search loop that builds on its own findings.

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
- **Identity Graph**: Interactive HTML visualization with color-coded nodes and confidence-weighted edges
- **Risk Assessment**: 5-level severity scoring across regulatory, financial, legal, reputational, and inconsistency categories
- **Confidence Scoring**: Every fact has a 0-1.0 confidence score with source URLs
- **Evaluation Framework**: 3 test personas with ground-truth benchmarking
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
```

### 5. Run evaluation
```bash
# All 3 personas
python evaluation/run_eval.py

# Single persona (1=Timothy, 2=Elizabeth Holmes, 3=Martin Shkreli)
python evaluation/run_eval.py 2
```

## Sample Output (Timothy Overturf)

**42 facts** extracted | **24 entities** discovered | **15 risk flags** | **51-node identity graph**

Key findings the agent uncovered autonomously:
- SEC charged Timothy Overturf and Sisu Capital with securities violations
- Unauthorized trades and breach of fiduciary duties
- Father (Hans Overturf) was a suspended investment adviser involved in client advice
- Sisu Capital invested client funds in thinly-traded bank stock
- Timothy founded the firm at age 18

## Project Structure

```
├── APPROACH.md              # Detailed design decisions and architecture
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
├── config/
│   └── settings.py          # Centralized configuration
├── agent/
│   ├── state.py             # Pydantic data models + LangGraph AgentState
│   ├── graph.py             # LangGraph assembly + LangSmith wiring
│   ├── nodes/
│   │   ├── query_planner.py    # Generates search queries (Groq)
│   │   ├── search_executor.py  # Runs Tavily searches with rate limiting
│   │   ├── fact_extractor.py   # Extracts structured facts (Groq)
│   │   ├── risk_analyzer.py    # Identifies risks (Gemini → Groq fallback)
│   │   ├── query_refiner.py    # Decides search continuation (Groq)
│   │   ├── graph_builder.py    # Builds identity graph (NetworkX + pyvis)
│   │   └── report_generator.py # Generates report (Gemini → Groq fallback)
│   ├── edges/
│   │   └── routing.py       # Conditional edge logic for search loop
│   └── prompts/
│       └── templates.py     # All 5 prompt templates
├── evaluation/
│   ├── eval_data.py         # 3 test personas + ground truth facts
│   ├── evaluator.py         # Metrics: recall, coverage, depth
│   └── run_eval.py          # Evaluation runner
├── outputs/
│   ├── graphs/              # Generated identity graph HTML files
│   ├── reports/             # Generated risk assessment reports
│   └── logs/                # Execution logs
├── app.py                   # Streamlit UI
└── main.py                  # CLI entry point
```

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Agent Orchestration | LangGraph | Stateful graph with conditional looping |
| Monitoring | LangSmith | Auto-traces all LLM calls |
| Model 1 (extraction) | Groq (Llama 3.3 70B) | Free, fast (~500 tok/s), reliable JSON |
| Model 2 (analysis) | Gemini 2.0 Flash | Free tier, strong analytical reasoning |
| Web Search | Tavily API | Built for AI agents, structured output |
| Graph Visualization | NetworkX + pyvis | Interactive HTML, no external services |
| UI | Streamlit | Rapid prototyping, live progress display |

## Evaluation

3 test personas with ground-truth facts, defined **before** building the agent:

| Persona | Facts | Entities | Purpose |
|---------|-------|----------|---------|
| Timothy Overturf | 1 | 2 | Primary target — hard (limited public info) |
| Elizabeth Holmes | 10 | 6 | Baseline — easy (well-documented) |
| Martin Shkreli | 8 | 5 | Depth test — medium (complex connections) |

Metrics: Recall, Category Coverage, Depth Score. See [APPROACH.md](APPROACH.md) for details.

## Design Decisions

See [APPROACH.md](APPROACH.md) for:
- Multi-model strategy (why Groq for extraction, Gemini for analysis)
- Consecutive search design (how iterations build on each other)
- Prompt engineering approach (anti-hallucination guards, structured output)
- Trade-offs table (what was chosen, what was considered, why)
- Production scalability roadmap
