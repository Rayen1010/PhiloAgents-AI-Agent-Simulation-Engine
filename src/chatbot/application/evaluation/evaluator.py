"""
Abstract Evaluator interface.

All concrete evaluators (Opik, custom, no-op) implement this interface.
The orchestrator references only Evaluator — it never imports a concrete class.
This allows swapping evaluation backends without touching application logic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationResult:
    """Structured result returned by every evaluator."""

    score: float
    """Overall quality score in [0, 1].  1.0 = perfect."""

    metrics: dict[str, float] = field(default_factory=dict)
    """Individual metric scores, e.g. {'hallucination': 0.9, 'relevance': 0.8}."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Extra info from the evaluation backend (trace ids, dataset refs, etc.)."""

    def __repr__(self) -> str:
        return (
            f"EvaluationResult(score={self.score:.3f}, metrics={self.metrics})"
        )


class Evaluator(ABC):
    """
    Abstract base for all evaluation backends.

    Implement this when adding a new evaluation provider.
    The interface is intentionally minimal — evaluate() is the only
    required method.
    """

    @abstractmethod
    def evaluate(
        self,
        question: str,
        answer: str,
        context: str = "",
        reference: str = "",
        **kwargs: Any,
    ) -> EvaluationResult:
        """
        Evaluate a single question-answer pair.

        Args
        ----
        question:   The user's input.
        answer:     The model's response.
        context:    Retrieved context used to generate the answer (optional).
        reference:  Ground-truth reference answer (optional).
        **kwargs:   Backend-specific parameters.

        Returns
        -------
        EvaluationResult with score and per-metric breakdown.
        """

    def evaluate_batch(
        self,
        examples: list[dict[str, str]],
        **kwargs: Any,
    ) -> list[EvaluationResult]:
        """
        Evaluate a list of examples.

        Default implementation calls evaluate() in a loop.
        Override for batched API calls.

        Each example dict should have keys: question, answer, context, reference.
        """
        return [self.evaluate(**example, **kwargs) for example in examples]