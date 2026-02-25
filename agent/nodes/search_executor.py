"""Node 2: Search Executor — runs Tavily searches with rate limiting."""

import time
import logging
from datetime import datetime

from tavily import TavilyClient

from config.settings import settings
from agent.state import AgentState, SearchResult

logger = logging.getLogger(__name__)


def search_executor(state: AgentState) -> dict:
    """Execute pending search queries via Tavily API.

    Processes queries that haven't been completed yet, with rate limiting
    and deduplication of results by URL.
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

    for sq in queries_to_run:
        try:
            logger.info(f"Searching: {sq.query}")
            response = client.search(
                query=sq.query,
                search_depth="advanced",
                max_results=5,
            )

            for result in response.get("results", []):
                url = result.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                new_results.append(SearchResult(
                    url=url,
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    score=result.get("score", 0.0),
                    query=sq.query,
                ))

            completed.append(sq.query)
            logs.append(
                f"[{datetime.now().isoformat()}] Search: '{sq.query}' → {len(response.get('results', []))} results"
            )

            # Rate limiting
            time.sleep(settings.search_rate_limit_seconds)

        except Exception as e:
            logger.error(f"Search failed for '{sq.query}': {e}")
            completed.append(sq.query)  # Mark as completed to avoid infinite retries
            logs.append(f"[{datetime.now().isoformat()}] Search FAILED: '{sq.query}' — {e}")

    return {
        "search_results": new_results,
        "completed_queries": completed,
        "execution_log": logs,
    }
