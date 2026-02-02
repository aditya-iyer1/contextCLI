from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass(frozen=True)
class Example:
    """Raw input from a dataset."""
    id: str
    context: str
    question: str
    answers: List[str]
    context_tokens: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Prediction:
    '''Model's response to an example'''
    example_id: str
    raw_output: str
    parsed_output: Optional[str] = None
    latency_ms: float = 0.0
    tfft_ms: float = 0.0 # Time to first token
    usage: Dict[str, int] = field(default_factory=dict) # prompt/completion tokens

@dataclass
class EvalRecord:
    '''Scores result of a prediction'''
    example_id: str
    context_tokens: int
    f1_score: float
    em_score: float
    failure_type: Optional[str] = None # e.g. "format_error", "refusal", "hallucination" 