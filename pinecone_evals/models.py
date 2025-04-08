"""Data models for the Pinecone Evals library."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, TypedDict


@dataclass
class Query:
    """Represents a search query."""
    text: str


class SearchHit(Dict[str, Any]):
    """
    Represents a single search result as a dictionary with completely flexible fields.
    
    This is simply a dictionary that can contain any fields needed for a search hit.
    Common fields include 'id' and 'text', but none are required.
    """
    pass


@dataclass
class SearchResult:
    """Collection of search hits for a query."""
    query: Query
    hits: List[SearchHit]


@dataclass
class EvalScore:
    """Evaluation scores for a single hit."""
    index: int
    hit_id: str
    eval_score: int  # 1-4 score
    relevant: bool  # True if score >= 3
    justification: Optional[str] = None


@dataclass
class EvalResult:
    """Evaluation results for a search query."""
    query: Query
    metrics: Dict[str, float]  # Contains ndcg, map, mrr
    hit_scores: List[EvalScore]
    usage: Dict[str, int]  # Token usage information