"""Evaluation metrics for the research agent.

Computes recall, precision, depth, and confidence calibration
by comparing agent output against ground-truth evaluation data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from agent.state import ExtractedFact, Entity, FactCategory


@dataclass
class EvalMetrics:
    """Evaluation metrics for a single persona run."""
    persona_name: str

    # Core metrics
    recall: float = 0.0              # ground_truth_found / total_ground_truth
    precision: float = 0.0           # correct_extracted / total_extracted (estimated)
    depth_score: float = 0.0         # non-obvious connections found
    category_coverage: float = 0.0   # categories covered / expected categories

    # Detail
    total_ground_truth: int = 0
    ground_truth_matched: int = 0
    total_extracted_facts: int = 0
    total_extracted_entities: int = 0
    categories_found: list[str] = field(default_factory=list)
    matched_facts: list[str] = field(default_factory=list)
    missed_facts: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Human-readable summary of metrics."""
        return (
            f"=== {self.persona_name} ===\n"
            f"  Recall:            {self.recall:.1%} ({self.ground_truth_matched}/{self.total_ground_truth})\n"
            f"  Category coverage: {self.category_coverage:.1%}\n"
            f"  Depth score:       {self.depth_score:.1%}\n"
            f"  Facts extracted:   {self.total_extracted_facts}\n"
            f"  Entities found:    {self.total_extracted_entities}\n"
            f"  Categories found:  {', '.join(self.categories_found)}\n"
            f"  Matched facts:     {', '.join(self.matched_facts) or 'None'}\n"
            f"  Missed facts:      {', '.join(self.missed_facts) or 'None'}\n"
        )


def evaluate_persona(
    persona: dict,
    extracted_facts: list[ExtractedFact],
    extracted_entities: list[Entity],
) -> EvalMetrics:
    """Evaluate agent output against ground-truth data for a persona.

    Uses fuzzy matching on subject-predicate-object triples to determine
    if ground truth facts were successfully discovered.

    Args:
        persona: Dict with 'name', 'ground_truth_facts', 'ground_truth_entities', 'expected_categories'
        extracted_facts: Facts output by the agent
        extracted_entities: Entities output by the agent

    Returns:
        EvalMetrics with computed scores
    """
    gt_facts: list[ExtractedFact] = persona.get("ground_truth_facts", [])
    expected_categories: list[FactCategory] = persona.get("expected_categories", [])

    metrics = EvalMetrics(
        persona_name=persona["name"],
        total_ground_truth=len(gt_facts),
        total_extracted_facts=len(extracted_facts),
        total_extracted_entities=len(extracted_entities),
    )

    # --- Recall: fuzzy match ground truth against extracted facts ---
    for gt in gt_facts:
        matched = _fuzzy_match_fact(gt, extracted_facts)
        if matched:
            metrics.ground_truth_matched += 1
            metrics.matched_facts.append(f"{gt.subject} {gt.predicate} {gt.object}")
        else:
            metrics.missed_facts.append(f"{gt.subject} {gt.predicate} {gt.object}")

    if gt_facts:
        metrics.recall = metrics.ground_truth_matched / len(gt_facts)

    # --- Category coverage ---
    found_categories = set()
    for f in extracted_facts:
        found_categories.add(f.category.value)
    metrics.categories_found = sorted(found_categories)

    if expected_categories:
        expected_set = {c.value for c in expected_categories}
        metrics.category_coverage = len(found_categories & expected_set) / len(expected_set)

    # --- Depth score: entities beyond the target and their direct company ---
    primary_names = {persona["name"].lower()}
    if persona.get("context"):
        # Extract company name from context like "CEO of Sisu Capital"
        for word in ["of", "at", "for"]:
            if word in persona["context"].lower():
                company = persona["context"].lower().split(word, 1)[1].strip()
                primary_names.add(company)

    non_obvious_entities = [
        e for e in extracted_entities
        if e.name.lower() not in primary_names
    ]
    # Depth score = ratio of non-obvious entities to total
    if extracted_entities:
        metrics.depth_score = len(non_obvious_entities) / len(extracted_entities)

    return metrics


def _fuzzy_match_fact(ground_truth: ExtractedFact, candidates: list[ExtractedFact]) -> bool:
    """Check if a ground truth fact is approximately matched by any candidate.

    Uses normalized string containment: if key terms from the ground truth
    appear in a candidate's subject+predicate+object, it's a match.
    """
    gt_terms = _extract_key_terms(
        f"{ground_truth.subject} {ground_truth.predicate} {ground_truth.object}"
    )

    for candidate in candidates:
        candidate_text = f"{candidate.subject} {candidate.predicate} {candidate.object}".lower()
        # Match if most key terms from ground truth appear in candidate
        matched_terms = sum(1 for term in gt_terms if term in candidate_text)
        if gt_terms and (matched_terms / len(gt_terms)) >= 0.5:
            return True

    return False


def _extract_key_terms(text: str) -> list[str]:
    """Extract meaningful terms from text, filtering stop words."""
    stop_words = {
        "a", "an", "the", "is", "was", "were", "are", "of", "in", "to",
        "for", "and", "or", "by", "at", "on", "from", "with", "as",
    }
    words = text.lower().split()
    return [w for w in words if w not in stop_words and len(w) > 2]
