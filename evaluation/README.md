# Evaluation Sets

Three test persona profiles with expected findings for evaluating the AI Research Agent.

## Persona 1: Timothy Overturf (Primary Test Case)
- **Context**: CEO of Sisu Capital
- **Difficulty**: Medium — SEC enforcement action provides clear trail
- **Expected file**: `persona_1_timothy_overturf.json`

## Persona 2: Elizabeth Holmes
- **Context**: Founder of Theranos
- **Difficulty**: Easy — well-documented fraud case
- **Expected file**: `persona_2_elizabeth_holmes.json`

## Persona 3: Martin Shkreli
- **Context**: Former CEO of Turing Pharmaceuticals
- **Difficulty**: Medium — multiple fraud charges, complex entity network
- **Expected file**: `persona_3_martin_shkreli.json`

## How to Run Evaluation

```bash
python evaluation/run_eval.py --persona 1 --max-iterations 3
```

Each persona file contains:
- `target_name`: The person to investigate
- `target_context`: Brief context
- `expected_entities`: Entities the agent should discover
- `expected_facts`: Key facts that should be extracted
- `expected_risks`: Risk flags that should be identified
- `evaluation_criteria`: Specific checkpoints for scoring
