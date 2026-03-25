"""FastAPI backend — bridges the LangGraph agent to the Next.js frontend via SSE."""

import json
import uuid
import asyncio
import threading
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

from agent.graph import build_research_graph, create_initial_state
from config.settings import settings
from demo_data import (
    DEMO_TARGET_NAME, DEMO_TARGET_CONTEXT,
    DEMO_FACTS, DEMO_ENTITIES, DEMO_RISK_FLAGS,
    DEMO_REPORT, DEMO_EXECUTION_LOG, DEMO_PIPELINE_STEPS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Research Agent API", version="1.0.0")

import os as _os
_allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# Allow the deployed Vercel frontend
if _os.getenv("FRONTEND_URL"):
    _allowed_origins.append(_os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://frontend(-[a-z0-9]+)?-masst\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# In-memory store for completed investigations
investigations: dict[str, dict] = {}

# List-type state keys that should be extended (not overwritten)
_LIST_KEYS = {
    "search_queries", "search_results", "completed_queries",
    "entities", "facts", "risk_flags", "execution_log",
}


class InvestigateRequest(BaseModel):
    target_name: str
    target_context: str = ""
    max_iterations: int = 5


def _serialize(obj) -> dict | str | list:
    """Serialize Pydantic models and enums to JSON-safe dicts."""
    if hasattr(obj, "model_dump"):
        d = obj.model_dump()
        # Convert enum values
        for k, v in d.items():
            if hasattr(v, "value"):
                d[k] = v.value
        return d
    if hasattr(obj, "value"):
        return obj.value
    return obj


def _serialize_list(items: list) -> list:
    return [_serialize(item) for item in items]


def _sse_event(event_type: str, data: dict) -> str:
    """Format an SSE event string."""
    return f"event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n"


def _merge_into(accumulated: dict, node_output: dict):
    """Merge a node's output into accumulated state (same logic as app.py)."""
    for key, value in node_output.items():
        if key in _LIST_KEYS and isinstance(value, list):
            existing = accumulated.get(key, [])
            existing_ids = set()
            for item in existing:
                item_id = getattr(item, "id", None)
                if item_id is None and isinstance(item, dict):
                    item_id = item.get("id")
                if item_id:
                    existing_ids.add(item_id)

            for item in value:
                item_id = getattr(item, "id", None)
                if item_id is None and isinstance(item, dict):
                    item_id = item.get("id")
                if item_id and item_id in existing_ids:
                    continue
                if isinstance(item, str) and item in existing:
                    continue
                existing.append(item)

            accumulated[key] = existing
        else:
            accumulated[key] = value


@app.post("/api/investigate")
async def investigate(req: InvestigateRequest):
    """Start an investigation and stream results via SSE."""
    investigation_id = str(uuid.uuid4())

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def run_agent():
            """Run the LangGraph agent in a background thread."""
            try:
                graph = build_research_graph()
                initial_state = create_initial_state(
                    req.target_name, req.target_context, req.max_iterations
                )
                accumulated: dict = {}
                node_count = 0

                for step in graph.stream(initial_state):
                    node_name = list(step.keys())[0]
                    node_output = step[node_name]
                    node_count += 1

                    # Merge into accumulated state
                    _merge_into(accumulated, node_output)

                    # Send node_start event
                    asyncio.run_coroutine_threadsafe(
                        queue.put(_sse_event("node_start", {
                            "node": node_name,
                            "iteration": accumulated.get("iteration", 0),
                            "progress": min(node_count / (7 * req.max_iterations), 0.95),
                        })),
                        loop,
                    )

                    # Send log events
                    for log_line in node_output.get("execution_log", []):
                        asyncio.run_coroutine_threadsafe(
                            queue.put(_sse_event("log", {"message": log_line})),
                            loop,
                        )

                    # Send incremental data updates based on node type
                    if "facts" in node_output and node_output["facts"]:
                        asyncio.run_coroutine_threadsafe(
                            queue.put(_sse_event("facts_update", {
                                "facts": _serialize_list(node_output["facts"]),
                                "total": len(accumulated.get("facts", [])),
                            })),
                            loop,
                        )

                    if "entities" in node_output and node_output["entities"]:
                        asyncio.run_coroutine_threadsafe(
                            queue.put(_sse_event("entities_update", {
                                "entities": _serialize_list(node_output["entities"]),
                                "total": len(accumulated.get("entities", [])),
                            })),
                            loop,
                        )

                    if "risk_flags" in node_output and node_output["risk_flags"]:
                        asyncio.run_coroutine_threadsafe(
                            queue.put(_sse_event("risks_update", {
                                "risk_flags": _serialize_list(node_output["risk_flags"]),
                                "total": len(accumulated.get("risk_flags", [])),
                            })),
                            loop,
                        )

                # Build final result
                result = {
                    "id": investigation_id,
                    "target_name": req.target_name,
                    "target_context": req.target_context,
                    "facts": _serialize_list(accumulated.get("facts", [])),
                    "entities": _serialize_list(accumulated.get("entities", [])),
                    "risk_flags": _serialize_list(accumulated.get("risk_flags", [])),
                    "report": accumulated.get("report", ""),
                    "graph_html": accumulated.get("graph_html", ""),
                    "iteration": accumulated.get("iteration", 0),
                    "execution_log": accumulated.get("execution_log", []),
                }

                # Store for later retrieval
                investigations[investigation_id] = result

                asyncio.run_coroutine_threadsafe(
                    queue.put(_sse_event("complete", {"result": result})),
                    loop,
                )

            except Exception as e:
                logger.error(f"Investigation failed: {e}")
                asyncio.run_coroutine_threadsafe(
                    queue.put(_sse_event("error", {"message": str(e)})),
                    loop,
                )
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        # Start agent in background thread
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

        # Yield SSE events from queue
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/investigations/{investigation_id}")
async def get_investigation(investigation_id: str):
    """Retrieve a completed investigation by ID."""
    if investigation_id not in investigations:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigations[investigation_id]


@app.get("/api/health")
async def health():
    """Health check with API key status."""
    return {
        "status": "ok",
        "keys": {
            "groq": bool(settings.groq_api_key),
            "gemini": bool(settings.google_api_key),
            "tavily": bool(settings.tavily_api_key),
            "langsmith": bool(settings.langchain_api_key),
        },
    }


@app.post("/api/demo")
async def demo_investigate():
    """Stream a pre-built demo investigation via SSE — no API credits used."""
    investigation_id = str(uuid.uuid4())

    async def demo_stream():
        # Map log lines to pipeline steps for realistic timing
        log_idx = 0
        logs_per_step = len(DEMO_EXECUTION_LOG) // len(DEMO_PIPELINE_STEPS)

        for i, (node, iteration, progress) in enumerate(DEMO_PIPELINE_STEPS):
            # node_start event
            yield _sse_event("node_start", {
                "node": node,
                "iteration": iteration,
                "progress": progress,
            })
            await asyncio.sleep(0.3)

            # Send log lines for this step
            step_end = min(log_idx + logs_per_step + 1, len(DEMO_EXECUTION_LOG))
            for j in range(log_idx, step_end):
                yield _sse_event("log", {"message": DEMO_EXECUTION_LOG[j]})
                await asyncio.sleep(0.15)
            log_idx = step_end

            # Send data updates at appropriate pipeline stages
            if node == "fact_extractor" and iteration == 0:
                yield _sse_event("facts_update", {
                    "facts": DEMO_FACTS[:15],
                    "total": 15,
                })
                yield _sse_event("entities_update", {
                    "entities": DEMO_ENTITIES[:10],
                    "total": 10,
                })
            elif node == "fact_extractor" and iteration == 1:
                yield _sse_event("facts_update", {
                    "facts": DEMO_FACTS[15:33],
                    "total": 33,
                })
                yield _sse_event("entities_update", {
                    "entities": DEMO_ENTITIES[10:18],
                    "total": 18,
                })
            elif node == "fact_extractor" and iteration == 2:
                yield _sse_event("facts_update", {
                    "facts": DEMO_FACTS[33:],
                    "total": len(DEMO_FACTS),
                })
                yield _sse_event("entities_update", {
                    "entities": DEMO_ENTITIES[18:],
                    "total": len(DEMO_ENTITIES),
                })
            elif node == "risk_analyzer" and iteration == 0:
                yield _sse_event("risks_update", {
                    "risk_flags": DEMO_RISK_FLAGS[:4],
                    "total": 4,
                })
            elif node == "risk_analyzer" and iteration == 1:
                yield _sse_event("risks_update", {
                    "risk_flags": DEMO_RISK_FLAGS[4:7],
                    "total": 7,
                })
            elif node == "risk_analyzer" and iteration == 2:
                yield _sse_event("risks_update", {
                    "risk_flags": DEMO_RISK_FLAGS[7:],
                    "total": len(DEMO_RISK_FLAGS),
                })

            await asyncio.sleep(0.2)

        # Flush remaining log lines
        for j in range(log_idx, len(DEMO_EXECUTION_LOG)):
            yield _sse_event("log", {"message": DEMO_EXECUTION_LOG[j]})
            await asyncio.sleep(0.1)

        # Final complete event
        result = {
            "id": investigation_id,
            "target_name": DEMO_TARGET_NAME,
            "target_context": DEMO_TARGET_CONTEXT,
            "facts": DEMO_FACTS,
            "entities": DEMO_ENTITIES,
            "risk_flags": DEMO_RISK_FLAGS,
            "report": DEMO_REPORT,
            "graph_html": "",
            "iteration": 3,
            "execution_log": DEMO_EXECUTION_LOG,
        }
        investigations[investigation_id] = result
        yield _sse_event("complete", {"result": result})

    return StreamingResponse(
        demo_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
