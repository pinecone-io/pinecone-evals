"""Data models for the Pinecone Evals library."""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypedDict, Iterator


@dataclass
class Query:
    """Represents a search query."""

    text: str
    id: Optional[str] = None


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
class HitScore:
    """
    Alias for EvalPassage for backward compatibility.
    This represents the evaluation scores for a single hit.
    """

    index: int
    hit_id: str
    eval_score: int  # 1-4 score
    relevant: bool  # True if score >= 3
    eval_text: str
    fields: Dict[str, Any]
    justification: Optional[str] = None


# Keep the original name but make it an alias to HitScore
EvalPassage = HitScore


@dataclass
class EvalSearch:
    """Evaluation results for a search query."""

    query: Query
    metrics: Dict[str, float]  # Contains ndcg, map, mrr
    hit_scores: List[HitScore]
    usage: Dict[str, int]  # Token usage information


@dataclass
class QuerySet:
    """A collection of queries that can be used for evaluation."""

    queries: List[Query] = field(default_factory=list)
    _query_map: Dict[str, Query] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Build query map for lookup by ID."""
        for query in self.queries:
            if query.id:
                self._query_map[query.id] = query
    
    def add_query(self, query: Query) -> Query:
        """
        Add a query to the set.
        
        Args:
            query: Query to add. If it doesn't have an ID, one will be assigned.
            
        Returns:
            The query with an ID assigned if it didn't have one.
        """
        if not query.id:
            query.id = str(uuid.uuid4())
        
        self.queries.append(query)
        self._query_map[query.id] = query
        return query
    
    def add_queries(self, queries: List[Query]) -> List[Query]:
        """
        Add multiple queries to the set.
        
        Args:
            queries: List of queries to add. Any without IDs will have them assigned.
            
        Returns:
            The list of queries with IDs assigned where needed.
        """
        for query in queries:
            self.add_query(query)
        return queries
    
    def get_query(self, query_id: str) -> Optional[Query]:
        """Get a query by its ID."""
        return self._query_map.get(query_id)
    
    def __len__(self) -> int:
        return len(self.queries)
    
    def __iter__(self) -> Iterator[Query]:
        return iter(self.queries)
    
    @classmethod
    def from_texts(cls, texts: List[str]) -> 'QuerySet':
        """Create a QuerySet from a list of query texts."""
        return cls(queries=[Query(text=text) for text in texts])
