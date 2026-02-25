# AI Research Agent — Autonomous Due Diligence

An autonomous research agent that investigates individuals for due diligence purposes. Built with LangGraph, it autonomously searches the web, extracts facts, identifies risks, maps connections, and generates identity graphs.

## Features

- **Multi-Model AI**: Groq (Llama 3.3 70B) for fast extraction + Gemini 2.5 Flash for deep risk analysis
- **Consecutive Search**: Iteratively discovers entities and refines queries
- **Identity Graph**: Interactive HTML visualization of connection networks
- **Risk Assessment**: Automated flagging of red flags and inconsistencies
- **Evaluation Framework**: 3 test personas with ground-truth benchmarking
- **LangSmith Tracing**: Full observability of every agent step

## Architecture

```
Query Planner → Search Executor → Fact Extractor → Risk Analyzer
       ↑                                                  │
       └──── Query Refiner ←──────────────────────────────┘
                    │
                    ↓ (when done)
           Graph Builder → Report Generator → END
```

## Quick Start

### 1. Clone and setup
```bash
git clone <repo-url>
cd deriv-ai-research-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env with your keys:
#   GROQ_API_KEY     — https://console.groq.com/keys
#   GOOGLE_API_KEY   — https://aistudio.google.com/apikey
#   TAVILY_API_KEY   — https://tavily.com
#   LANGCHAIN_API_KEY — https://smith.langchain.com (optional)
```

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

## Project Structure

```
├── APPROACH.md              # Design decisions and trade-offs
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
├── config/
│   └── settings.py          # Centralized configuration
├── agent/
│   ├── state.py             # Data models + LangGraph state
│   ├── graph.py             # LangGraph assembly
│   ├── nodes/
│   │   ├── query_planner.py    # Generates search queries (Groq)
│   │   ├── search_executor.py  # Runs Tavily searches
│   │   ├── fact_extractor.py   # Extracts structured facts (Groq)
│   │   ├── risk_analyzer.py    # Identifies risks (Gemini)
│   │   ├── query_refiner.py    # Decides search continuation (Groq)
│   │   ├── graph_builder.py    # Builds identity graph (NetworkX)
│   │   └── report_generator.py # Generates report (Gemini)
│   ├── edges/
│   │   └── routing.py       # Conditional edge logic
│   └── prompts/
│       └── templates.py     # All prompt templates
├── evaluation/
│   ├── eval_data.py         # 3 test personas + ground truth
│   ├── evaluator.py         # Metrics computation
│   └── run_eval.py          # Evaluation runner
├── app.py                   # Streamlit UI
└── main.py                  # CLI entry point
```

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Agent | LangGraph | Assignment requirement, excellent for stateful workflows |
| Monitoring | LangSmith | Assignment requirement, full trace visibility |
| Model 1 | Groq (Llama 3.3 70B) | Free, fast (~500 tok/s), reliable JSON output |
| Model 2 | Gemini 2.5 Flash | Free tier, strong analytical reasoning |
| Search | Tavily | Built for AI agents, structured output |
| Graph | NetworkX + pyvis | Zero setup, interactive HTML visualization |
| UI | Streamlit | Rapid prototyping, live demo |

## Evaluation

The agent is benchmarked against 3 personas with known ground-truth facts:

| Persona | Purpose | Expected Difficulty |
|---------|---------|-------------------|
| Timothy Overturf | Primary test case | Hard (limited public info) |
| Elizabeth Holmes | Baseline test | Easy (well-documented) |
| Martin Shkreli | Depth test | Medium (complex connections) |

Metrics: Recall, Category Coverage, Depth Score

## Design Decisions

See [APPROACH.md](APPROACH.md) for detailed architectural decisions and trade-offs.
