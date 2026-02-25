"""Node 2: Search Executor — runs Tavily searches with rate limiting.

Uses concurrent execution to parallelize search queries for speed,
while still respecting API rate limits.
"""

import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from tavily import TavilyClient

from config.settings import settings
from agent.state import AgentState, SearchResult

logger = logging.getLogger(__name__)


def _run_single_search(client: TavilyClient, query: str) -> dict:
    """Execute a single Tavily search. Runs inside a thread."""
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
    )
    return {"query": query, "results": response.get("results", []), "error": None}


def search_executor(state: AgentState) -> dict:
    """Execute pending search queries via Tavily API.

    Processes queries that haven't been completed yet, running them
    concurrently (up to 3 in parallel) for speed. Deduplicates results by URL.
    """
    client = TavilyClient(api_key=settings.tavily_api_key)

    pending_queries = [
        q for q in state.get("search_queries", [])
        if q.query not in state.get("completed_queries", [])
    ]

    if not pending_queries:
        return {
            "execution_log": [f"[{datetime.now().isoformat()}] Search: No pending queries to execute"],
        }

    # Limit queries per iteration to avoid burning API quota
    queries_to_run = pending_queries[:settings.max_queries_per_iteration]
    new_results: list[SearchResult] = []
    completed: list[str] = []
    seen_urls = {r.url for r in state.get("search_results", [])}
    logs: list[str] = []

    # Run searches concurrently (max 3 workers to stay within rate limits)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_query = {
            executor.submit(_run_single_search, client, sq.query): sq
            for sq in queries_to_run
        }

        for future in as_completed(future_to_query):
            sq = future_to_query[future]
            try:
                result = future.result()
                for r in result["results"]:
                    url = r.get("url", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    new_results.append(SearchResult(
                        url=url,
                        title=r.get("title", ""),
                        content=r.get("content", ""),
                        score=r.get("score", 0.0),
                        query=sq.query,
                    ))

                completed.append(sq.query)
                logs.append(
                    f"[{datetime.now().isoformat()}] Search: '{sq.query}' → {len(result['results'])} results"
                )

            except Exception as e:
                logger.error(f"Search failed for '{sq.query}': {e}")
                completed.append(sq.query)
                logs.append(f"[{datetime.now().isoformat()}] Search FAILED: '{sq.query}' — {e}")

    return {
        "search_results": new_results,
        "completed_queries": completed,
        "execution_log": logs,
    }
