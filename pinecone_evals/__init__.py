"""
Pinecone Evals: A library for evaluating vector search results.

This library provides tools to evaluate and compare search result relevance.
"""

from .client import PineconeEval
from .evaluator import SearchEvaluator
from .models import (
    Query,
    SearchHit as Hit,
    SearchResult,
    EvalPassage,
    EvalSearch,
    HitScore,
)

__version__ = "0.1.0"

__all__ = [
    "SearchEvaluator",
    "PineconeEval",
    "Query",
    "Hit",
    "SearchResult",
    "EvalSearch",
    "EvalPassage",
    "HitScore",
]
