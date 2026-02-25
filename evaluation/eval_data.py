"""Evaluation data: 3 test personas with ground-truth facts.

These personas are used to benchmark the agent's performance before
and after improvements. Each persona has a set of known facts that
the agent should be able to discover.

Persona selection rationale:
1. Timothy Overturf (primary test case from assignment) — real target
2. Elizabeth Holmes (well-known, lots of public info) — easy baseline
3. Martin Shkreli (complex connections, controversies) — depth test
"""

from agent.state import ExtractedFact, Entity, EntityType, FactCategory


# ---------------------------------------------------------------------------
# Persona 1: Timothy Overturf — The actual assignment target
# ---------------------------------------------------------------------------
PERSONA_1 = {
    "name": "Timothy Overturf",
    "context": "CEO of Sisu Capital",
    "description": "Primary test case from assignment. A less public figure, tests the agent's ability to find information on individuals with limited online presence.",
    "ground_truth_facts": [
        ExtractedFact(
            subject="Timothy Overturf",
            predicate="is CEO of",
            object="Sisu Capital",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        # Additional ground truth facts should be populated after manual research
        # These serve as placeholders for the evaluation framework structure
    ],
    "ground_truth_entities": [
        Entity(name="Timothy Overturf", entity_type=EntityType.PERSON, description="Target individual"),
        Entity(name="Sisu Capital", entity_type=EntityType.ORGANIZATION, description="Company led by target"),
    ],
    "expected_categories": [
        FactCategory.PROFESSIONAL,
        FactCategory.FINANCIAL,
    ],
}


# ---------------------------------------------------------------------------
# Persona 2: Elizabeth Holmes — Easy baseline (lots of public info)
# ---------------------------------------------------------------------------
PERSONA_2 = {
    "name": "Elizabeth Holmes",
    "context": "Founder of Theranos",
    "description": "Well-documented public figure. Agent should achieve high recall. Tests basic search and extraction capabilities.",
    "ground_truth_facts": [
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="founded",
            object="Theranos",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="was convicted of",
            object="fraud",
            confidence=1.0,
            category=FactCategory.LEGAL,
        ),
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="attended",
            object="Stanford University",
            confidence=1.0,
            category=FactCategory.BIOGRAPHICAL,
        ),
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="was sentenced to",
            object="over 11 years in prison",
            confidence=1.0,
            category=FactCategory.LEGAL,
        ),
        ExtractedFact(
            subject="Theranos",
            predicate="was valued at",
            object="$9 billion",
            confidence=0.9,
            category=FactCategory.FINANCIAL,
        ),
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="partnered with",
            object="Walgreens",
            confidence=0.9,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Ramesh Balwani",
            predicate="was COO of",
            object="Theranos",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="was charged by",
            object="SEC",
            confidence=1.0,
            category=FactCategory.REGULATORY,
        ),
        ExtractedFact(
            subject="Theranos",
            predicate="claimed to revolutionize",
            object="blood testing technology",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Elizabeth Holmes",
            predicate="was exposed by",
            object="Wall Street Journal investigation by John Carreyrou",
            confidence=1.0,
            category=FactCategory.SOCIAL,
        ),
    ],
    "ground_truth_entities": [
        Entity(name="Elizabeth Holmes", entity_type=EntityType.PERSON, description="Founder of Theranos"),
        Entity(name="Theranos", entity_type=EntityType.ORGANIZATION, description="Blood testing startup"),
        Entity(name="Ramesh Balwani", entity_type=EntityType.PERSON, description="COO of Theranos"),
        Entity(name="Stanford University", entity_type=EntityType.ORGANIZATION, description="University"),
        Entity(name="Walgreens", entity_type=EntityType.ORGANIZATION, description="Pharmacy chain partner"),
        Entity(name="SEC", entity_type=EntityType.ORGANIZATION, description="Securities and Exchange Commission"),
    ],
    "expected_categories": [
        FactCategory.PROFESSIONAL,
        FactCategory.LEGAL,
        FactCategory.FINANCIAL,
        FactCategory.BIOGRAPHICAL,
        FactCategory.REGULATORY,
        FactCategory.SOCIAL,
    ],
}


# ---------------------------------------------------------------------------
# Persona 3: Martin Shkreli — Complex connections, depth test
# ---------------------------------------------------------------------------
PERSONA_3 = {
    "name": "Martin Shkreli",
    "context": "Former CEO of Turing Pharmaceuticals",
    "description": "Complex network of companies, legal issues, and controversies. Tests the agent's ability to uncover non-obvious connections and trace corporate relationships.",
    "ground_truth_facts": [
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="was CEO of",
            object="Turing Pharmaceuticals",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="raised price of",
            object="Daraprim from $13.50 to $750 per pill",
            confidence=1.0,
            category=FactCategory.FINANCIAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="was convicted of",
            object="securities fraud",
            confidence=1.0,
            category=FactCategory.LEGAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="founded",
            object="Retrophin",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="was sentenced to",
            object="seven years in prison",
            confidence=1.0,
            category=FactCategory.LEGAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="purchased",
            object="Wu-Tang Clan album Once Upon a Time in Shaolin",
            confidence=0.9,
            category=FactCategory.SOCIAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="founded",
            object="MSMB Capital Management",
            confidence=1.0,
            category=FactCategory.PROFESSIONAL,
        ),
        ExtractedFact(
            subject="Martin Shkreli",
            predicate="was sued by",
            object="Retrophin for $65 million",
            confidence=0.9,
            category=FactCategory.LEGAL,
        ),
    ],
    "ground_truth_entities": [
        Entity(name="Martin Shkreli", entity_type=EntityType.PERSON, description="Target individual"),
        Entity(name="Turing Pharmaceuticals", entity_type=EntityType.ORGANIZATION, description="Pharma company"),
        Entity(name="Retrophin", entity_type=EntityType.ORGANIZATION, description="Biotech company he founded"),
        Entity(name="MSMB Capital Management", entity_type=EntityType.ORGANIZATION, description="Hedge fund he founded"),
        Entity(name="Daraprim", entity_type=EntityType.EVENT, description="Drug whose price was raised"),
    ],
    "expected_categories": [
        FactCategory.PROFESSIONAL,
        FactCategory.LEGAL,
        FactCategory.FINANCIAL,
        FactCategory.SOCIAL,
    ],
}


# All personas for evaluation
PERSONAS = [PERSONA_1, PERSONA_2, PERSONA_3]
