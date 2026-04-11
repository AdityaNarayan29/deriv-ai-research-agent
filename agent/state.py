"""Data models and LangGraph state schema for the research agent."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    EVENT = "event"
    FILING = "filing"
    LOCATION = "location"


class FactCategory(str, Enum):
    BIOGRAPHICAL = "biographical"
    PROFESSIONAL = "professional"
    FINANCIAL = "financial"
    LEGAL = "legal"
    SOCIAL = "social"
    REGULATORY = "regulatory"


class RiskCategory(str, Enum):
    REGULATORY = "regulatory"
    REPUTATIONAL = "reputational"
    FINANCIAL = "financial"
    LEGAL = "legal"
    INCONSISTENCY = "inconsistency"


class RiskSeverity(int, Enum):
    LOW = 1
    MODERATE = 2
    ELEVATED = 3
    HIGH = 4
    CRITICAL = 5


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class SearchQuery(BaseModel):
    """A search query to execute."""
    query: str
    category: FactCategory = FactCategory.PROFESSIONAL
    rationale: str = ""


class SearchResult(BaseModel):
    """A single search result from Tavily."""
    url: str
    title: str
    content: str
    score: float = 0.0
    query: str = ""


class Entity(BaseModel):
    """A discovered entity (person, organization, etc.)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    entity_type: EntityType
    description: str = ""
    first_seen_query: str = ""
    investigated: bool = False


class ExtractedFact(BaseModel):
    """A structured fact extracted from search results."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    subject: str
    predicate: str
    object: str
    source_url: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    category: FactCategory = FactCategory.PROFESSIONAL
    source_query: str = ""


class RiskFlag(BaseModel):
    """A risk or red flag identified by analysis."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    severity: RiskSeverity = RiskSeverity.LOW
    category: RiskCategory = RiskCategory.REPUTATIONAL
    evidence_fact_ids: list[str] = Field(default_factory=list)
    recommendation: str = ""


# ---------------------------------------------------------------------------
# LangGraph State — uses TypedDict for LangGraph compatibility
# ---------------------------------------------------------------------------

from typing import TypedDict


def _get_id(item) -> str | None:
    """Extract the 'id' field from a Pydantic model or dict, if present."""
    return getattr(item, "id", None) or (item.get("id") if isinstance(item, dict) else None)


def _merge_lists(existing: list, new: list) -> list:
    """Merge two lists, deduplicating by 'id' field if present.

    On ID collision, the NEW item replaces the existing one
    (last-write-wins). This allows nodes to emit updates to
    previously-seen objects — risk_analyzer uses it to apply confidence
    adjustments to facts, search_executor uses it to toggle
    entity.investigated.

    Items without an 'id' field accumulate unconditionally (no dedup).
    Dict preserves insertion order, so existing items keep their
    relative position even when replaced.
    """
    if not new:
        return existing
    if not existing:
        return new

    # Index existing items by ID (preserves insertion order)
    by_id: dict[str, object] = {}
    no_id: list = []
    for item in existing:
        item_id = _get_id(item)
        if item_id:
            by_id[item_id] = item
        else:
            no_id.append(item)

    # Merge new items — last-write-wins on ID collision
    for item in new:
        item_id = _get_id(item)
        if item_id:
            by_id[item_id] = item  # replaces existing or adds new
        else:
            no_id.append(item)

    return list(by_id.values()) + no_id


def _merge_strings(existing: list[str], new: list[str]) -> list[str]:
    """Merge string lists, deduplicating."""
    seen = set(existing)
    merged = list(existing)
    for s in new:
        if s not in seen:
            seen.add(s)
            merged.append(s)
    return merged


class AgentState(TypedDict):
    """The state that flows through the LangGraph research agent."""

    # Input
    target_name: str
    target_context: str

    # Search state
    search_queries: Annotated[list[SearchQuery], _merge_lists]
    search_results: Annotated[list[SearchResult], _merge_lists]
    completed_queries: Annotated[list[str], _merge_strings]

    # Extraction state
    entities: Annotated[list[Entity], _merge_lists]
    facts: Annotated[list[ExtractedFact], _merge_lists]
    risk_flags: Annotated[list[RiskFlag], _merge_lists]

    # Control flow
    iteration: int
    max_iterations: int
    should_continue: bool

    # Outputs
    graph_html: str
    report: str
    execution_log: Annotated[list[str], _merge_strings]
