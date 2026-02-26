"""Shared LLM retry utility with exponential backoff for rate-limit (429) errors."""

import time
import logging
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Strings that indicate a rate-limit / quota error in exception messages
_RATE_LIMIT_MARKERS = ("429", "rate_limit", "rate limit", "resource_exhausted", "quota")

MAX_RETRIES = 3
BASE_DELAY = 2.0  # seconds


def _is_rate_limit_error(exc: Exception) -> bool:
    """Check if an exception is a rate-limit / quota error."""
    msg = str(exc).lower()
    return any(marker in msg for marker in _RATE_LIMIT_MARKERS)


def invoke_with_retry(
    llm,
    prompt: str,
    *,
    label: str = "LLM",
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY,
):
    """
    Invoke an LLM with automatic retry + exponential backoff for 429 errors.

    Non-rate-limit errors are raised immediately (so the caller can try
    the next model in the fallback chain).

    Returns the LLM response on success; raises on permanent failure.
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return llm.invoke([HumanMessage(content=prompt)])
        except Exception as e:
            last_error = e

            if _is_rate_limit_error(e):
                delay = base_delay * (2 ** (attempt - 1))  # 2s, 4s, 8s
                logger.warning(
                    f"{label}: Rate-limited (attempt {attempt}/{max_retries}), "
                    f"retrying in {delay:.0f}s — {e}"
                )
                time.sleep(delay)
                continue
            else:
                # Non-rate-limit error — let caller handle fallback
                raise

    # All retries exhausted for rate-limit errors
    logger.error(f"{label}: Rate limit retries exhausted after {max_retries} attempts")
    raise last_error  # type: ignore[misc]
