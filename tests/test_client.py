"""Tests for the PineconeEval client."""

import unittest
from unittest.mock import MagicMock, patch

from pinecone_evals.client import PineconeEval
from pinecone_evals.models import Query
from .mock import MockPineconeEval


class TestPineconeEvalClient(unittest.TestCase):
    """Test cases for the PineconeEval client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = PineconeEval(api_key="test_api_key")

        # Sample test data
        self.test_query = Query(text="test query")
        self.test_hits = [
            {"id": "hit1", "text": "Test hit 1"},
            {"id": "hit2", "text": "Test hit 2"}
        ]

        # Mock API response
        self.mock_response = {
            "hits": [
                {
                    "index": 0,
                    "fields": {
                        "id": "hit1",
                        "text": "Test hit 1"
                    },
                    "relevant": True,
                    "score": 4,
                    "justification": "Test justification"
                },
                {
                    "index": 1,
                    "fields": {
                        "id": "hit2",
                        "text": "Test hit 2"
                    },
                    "relevant": False,
                    "score": 2,
                    "justification": "Test justification"
                }
            ],
            "metrics": {
                "ndcg": 0.8,
                "map": 0.7,
                "mrr": 0.9
            },
            "usage": {
                "evaluation_input_tokens": 100,
                "evaluation_output_tokens": 50
            }
        }

    @patch("requests.Session.post")
    def test_evaluate_search(self, mock_post):
        """Test the evaluate_search method with mocked API response."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_response
        mock_post.return_value = mock_response

        # Call the method under test
        result = self.client.evaluate_search(
            query=self.test_query,
            hits=self.test_hits
        )

        # Verify the API was called with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]["json"]
        self.assertEqual(call_args["query"]["inputs"]["text"], "test query")
        self.assertEqual(len(call_args["hits"]), 2)

        # Verify the result structure
        self.assertEqual(result.query, self.test_query)
        self.assertEqual(len(result.hit_scores), 2)
        self.assertEqual(result.hit_scores[0].hit_id, "hit1")
        self.assertEqual(result.hit_scores[0].eval_score, 4)
        self.assertEqual(result.hit_scores[0].relevant, True)

        # Verify metrics
        self.assertEqual(result.metrics["ndcg"], 0.8)
        self.assertEqual(result.metrics["map"], 0.7)
        self.assertEqual(result.metrics["mrr"], 0.9)

        # Verify usage data
        self.assertEqual(result.usage["evaluation_input_tokens"], 100)


class TestMockPineconeEvalClient(unittest.TestCase):
    """Test cases for the MockPineconeEval client."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockPineconeEval()

        # Sample test data for general testing
        self.test_query = Query(text="specific unique phrase")
        self.test_hits = [
            {"id": "hit1", "text": "Document containing the specific unique phrase we're looking for"},
            {"id": "hit2", "text": "Document without any matching terms"}
        ]

    def test_mock_evaluate_search(self):
        """Test the mock evaluation functionality."""
        # Call the method under test
        result = self.mock_client.evaluate_search(
            query=self.test_query,
            hits=self.test_hits
        )

        # Verify the result structure
        self.assertEqual(result.query, self.test_query)
        self.assertEqual(len(result.hit_scores), 2)

        # Verify relevance determination
        self.assertTrue(result.hit_scores[0].relevant)  # Should be relevant due to keyword match
        self.assertFalse(result.hit_scores[1].relevant)  # Should not be relevant

        # Verify metrics exist
        self.assertIn("ndcg", result.metrics)
        self.assertIn("map", result.metrics)
        self.assertIn("mrr", result.metrics)

        # Verify usage data
        self.assertIn("evaluation_input_tokens", result.usage)
        self.assertIn("evaluation_output_tokens", result.usage)

    def test_different_queries(self):
        """Test that different queries produce different relevance judgments."""
        # Create hits with more specific text content for better testing
        specific_hits = [
            {"id": "hit1", "text": "This is about machine learning algorithms"},
            {"id": "hit2", "text": "Document about databases and data storage"}
        ]

        # Query that should only match the first hit
        query1 = Query(text="machine learning")
        result1 = self.mock_client.evaluate_search(query=query1, hits=specific_hits)

        # Verify first hit is relevant, second is not
        self.assertTrue(result1.hit_scores[0].relevant)
        self.assertFalse(result1.hit_scores[1].relevant)

        # Query that should only match the second hit
        query2 = Query(text="databases")
        result2 = self.mock_client.evaluate_search(query=query2, hits=specific_hits)

        # Verify first hit is not relevant, second is relevant
        self.assertFalse(result2.hit_scores[0].relevant)
        self.assertTrue(result2.hit_scores[1].relevant)

    def test_custom_fields(self):
        """Test that the mock client works with custom fields."""
        # Create hits with custom fields
        custom_hits = [
            {
                "id": "hit1",
                "text": "Main content text",
                "title": "Important document title",
                "metadata": {"author": "John Doe", "year": 2023}
            },
            {
                "id": "hit2",
                "chunk_text": "This is alternative text field",
                "custom_field": "Custom value"
            }
        ]

        # Query that should match custom fields
        query = Query(text="document title")
        result = self.mock_client.evaluate_search(query=query, hits=custom_hits)

        # Verify the hits were processed correctly
        self.assertEqual(len(result.hit_scores), 2)

        # Verify first hit is relevant (matching "title" field)
        self.assertTrue(result.hit_scores[0].relevant)


if __name__ == "__main__":
    unittest.main()
