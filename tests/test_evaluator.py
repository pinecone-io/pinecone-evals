"""Tests for the SearchEvaluator class."""

import unittest
from unittest.mock import MagicMock, patch

from pinecone_evals.models import (
    Query,
    SearchHit,
    SearchResult,
    EvalSearch,
    EvalPassage,
)
from pinecone_evals.evaluator import SearchEvaluator


class TestSearchEvaluator(unittest.TestCase):
    """Test cases for the SearchEvaluator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.evaluator = SearchEvaluator(self.mock_client)

        # Sample test data
        self.test_queries = [Query(text="query1"), Query(text="query2")]

        # Mock search function
        def mock_search(query):
            return SearchResult(
                query=query,
                hits=[
                    SearchHit(id="hit1", text="Test hit 1"),
                    SearchHit(id="hit2", text="Test hit 2"),
                ],
            )

        self.mock_search_fn = mock_search

        # Mock eval results
        self.mock_eval_result = EvalSearch(
            query=self.test_queries[0],
            metrics={"ndcg": 0.8, "map": 0.7, "mrr": 0.9},
            hit_scores=[
                EvalPassage(index=0, hit_id="hit1", eval_score=4, relevant=True),
                EvalPassage(index=1, hit_id="hit2", eval_score=2, relevant=False),
            ],
            usage={"evaluation_input_tokens": 100},
        )

        # Configure mock client to return the mock eval result
        self.mock_client.evaluate_search.return_value = self.mock_eval_result

    def test_evaluate_approach(self):
        """Test the evaluate_approach method."""
        # Call the method under test
        result = self.evaluator.evaluate_approach(
            name="test_approach",
            search_fn=self.mock_search_fn,
            queries=[self.test_queries[0]],  # Just use one query for simplicity
        )

        # Verify that the client's evaluate_search method was called
        self.mock_client.evaluate_search.assert_called_once()

        # Verify the result structure
        self.assertIn("metrics", result)
        self.assertIn("detailed_results", result)

        # Verify metrics calculation
        self.assertIn("ndcg", result["metrics"])
        self.assertEqual(result["metrics"]["ndcg"]["mean"], 0.8)

    def test_compare_approaches(self):
        """Test the compare_approaches method."""
        # Set up multiple approaches
        self.evaluator.evaluate_approach(
            name="approach1",
            search_fn=self.mock_search_fn,
            queries=[self.test_queries[0]],
        )

        # Configure second approach with different metrics
        self.mock_client.evaluate_search.return_value = EvalSearch(
            query=self.test_queries[0],
            metrics={"ndcg": 0.9, "map": 0.8, "mrr": 0.7},
            hit_scores=[
                EvalPassage(index=0, hit_id="hit1", eval_score=4, relevant=True),
                EvalPassage(index=1, hit_id="hit2", eval_score=4, relevant=True),
            ],
            usage={"evaluation_input_tokens": 100},
        )

        self.evaluator.evaluate_approach(
            name="approach2",
            search_fn=self.mock_search_fn,
            queries=[self.test_queries[0]],
        )

        # Call the method under test
        comparison = self.evaluator.compare_approaches()

        # Verify the comparison result
        self.assertIn("ndcg", comparison)
        self.assertEqual(comparison["ndcg"]["best_approach"], "approach2")
        self.assertEqual(comparison["map"]["best_approach"], "approach2")
        self.assertEqual(comparison["mrr"]["best_approach"], "approach1")

    def test_generate_report(self):
        """Test the generate_report method."""
        # Set up test data
        self.evaluator.evaluate_approach(
            name="approach1",
            search_fn=self.mock_search_fn,
            queries=[self.test_queries[0]],
        )

        # Call the method under test
        report = self.evaluator.generate_report()

        # Verify the report contains expected sections
        self.assertIn("# Search Evaluation Report", report)
        self.assertIn("## Comparison Summary", report)
        self.assertIn("| Metric |", report)

        # Verify metrics are included
        self.assertIn("ndcg", report)
        self.assertIn("map", report)
        self.assertIn("mrr", report)


if __name__ == "__main__":
    unittest.main()
