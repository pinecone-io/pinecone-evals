"""Mock implementation of the Pinecone Evals API client for testing."""

from typing import Dict, List, Any

from pinecone_evals.models import Query, SearchHit, EvalPassage, EvalSearch
from pinecone_evals.client import PineconeEval


class MockPineconeEval(PineconeEval):
    """
    Mock implementation of the PineconeEval client for testing.

    This client doesn't make actual API calls but simulates responses
    for testing purposes.
    """

    def __init__(self):
        # No API key or endpoint needed for the mock
        super().__init__(api_key="mock_api_key", endpoint="mock://pinecone.io/eval")

    def evaluate_search(
        self,
        query: Query,
        hits: List[SearchHit],
        fields: List[str] = None,
        debug: bool = False,
    ) -> EvalSearch:
        """
        Generate a mock evaluation result without making an API call.

        Args:
            query: The search query
            hits: List of search hits to evaluate
            fields: Fields to consider in evaluation (ignored in mock)
            debug: Enable detailed evaluation debugging (ignored in mock)

        Returns:
            Mocked EvalResult
        """
        # Generate mock response
        mock_response = self._generate_mock_response(query, hits)

        # Parse it the same way as the real client would
        return self._parse_response(query, mock_response)

    def _make_api_call(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override to avoid actual API calls."""
        # Instead of making an API call, generate a mock response
        query_text = request_data["query"]["inputs"]["text"]
        query = Query(text=query_text)
        hits = request_data["hits"]
        return self._generate_mock_response(query, hits)

    def _generate_mock_response(
        self, query: Query, hits: List[SearchHit]
    ) -> Dict[str, Any]:
        """Generate a mock eval response for testing."""
        mock_hits = []

        # Simple relevance simulation
        for i, hit in enumerate(hits):
            # Check all string fields for relevance matching
            query_words = query.text.lower().split()
            relevant = False

            # Check each field for relevance
            for field_name, field_value in hit.items():
                # Skip non-string fields
                if not isinstance(field_value, str):
                    continue

                # Check if any query word is in this field
                if any(word.lower() in field_value.lower() for word in query_words):
                    relevant = True
                    break

            # Create the mock hit response
            mock_hit = {
                "index": i,
                "fields": dict(hit),  # Copy all hit fields
                "relevant": relevant,
                "score": 4 if relevant else 2,
                "justification": "Mock justification for testing purposes",
            }
            mock_hits.append(mock_hit)

        # Calculate mock metrics based on relevance
        relevance_scores = [1.0 if hit["relevant"] else 0.0 for hit in mock_hits]
        metrics = self._calculate_mock_metrics(relevance_scores)

        return {
            "metrics": metrics,
            "hits": mock_hits,
            "usage": {"evaluation_input_tokens": 1000, "evaluation_output_tokens": 500},
        }

    def _calculate_mock_metrics(
        self, relevance_scores: List[float]
    ) -> Dict[str, float]:
        """Calculate mock metrics based on relevance scores."""
        if not relevance_scores:
            return {"ndcg": 0.0, "map": 0.0, "mrr": 0.0}

        # Simplified NDCG calculation
        ndcg = (
            sum(score / (i + 1) for i, score in enumerate(relevance_scores))
            / sum(1 / (i + 1) for i in range(len(relevance_scores)))
            if relevance_scores
            else 0
        )

        # First relevant position or 0 if none relevant
        first_relevant = next(
            (i + 1 for i, r in enumerate(relevance_scores) if r > 0), 0
        )
        mrr = 1 / first_relevant if first_relevant > 0 else 0

        # Simplified MAP calculation
        relevant_count = sum(relevance_scores)
        map_score = (
            sum(
                (sum(relevance_scores[: i + 1]) / (i + 1))
                * (1 if relevance_scores[i] > 0 else 0)
                for i in range(len(relevance_scores))
            )
            / relevant_count
            if relevant_count > 0
            else 0
        )

        return {"ndcg": ndcg, "map": map_score, "mrr": mrr}
