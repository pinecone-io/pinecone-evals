"""
Pinecone Evals: A library for evaluating vector search results.

This library provides tools to evaluate and compare search result relevance.
"""

from .models import Query, SearchHit, SearchResult, EvalScore, EvalResult
from .client import PineconeEval
from .mock import MockPineconeEval
from .evaluator import SearchEvaluator

__version__ = "0.1.0"