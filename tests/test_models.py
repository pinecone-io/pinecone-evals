"""Tests for the data models."""

import unittest

from pinecone_evals.models import Query, SearchHit, SearchResult, EvalScore, EvalResult


class TestModels(unittest.TestCase):
    """Test cases for the data models."""
    
    def test_query(self):
        """Test the Query model."""
        query = Query(text="test query")
        self.assertEqual(query.text, "test query")
    
    def test_search_hit(self):
        """Test the SearchHit model."""
        # Now SearchHit is just a dictionary
        hit = SearchHit({"id": "test_id", "text": "test text"})
        self.assertEqual(hit["id"], "test_id")
        self.assertEqual(hit["text"], "test text")
        
        # We can also create it with keyword arguments
        hit2 = SearchHit(id="test_id2", text="test text 2", custom_field="custom value")
        self.assertEqual(hit2["id"], "test_id2")
        self.assertEqual(hit2["text"], "test text 2")
        self.assertEqual(hit2["custom_field"], "custom value")
        
        # Test dictionary-like behavior
        hit["new_field"] = "new value"
        self.assertEqual(hit["new_field"], "new value")
        self.assertTrue("id" in hit)
        self.assertTrue("new_field" in hit)
    
    def test_search_result(self):
        """Test the SearchResult model."""
        query = Query(text="test query")
        hits = [
            {"id": "hit1", "text": "Test hit 1"},
            {"id": "hit2", "text": "Test hit 2"}
        ]
        
        result = SearchResult(query=query, hits=hits)
        self.assertEqual(result.query, query)
        self.assertEqual(len(result.hits), 2)
        self.assertEqual(result.hits[0]["id"], "hit1")
    
    def test_eval_score(self):
        """Test the EvalScore model."""
        score = EvalScore(
            index=0,
            hit_id="test_id",
            eval_score=4,
            relevant=True,
            justification="Test justification"
        )
        
        self.assertEqual(score.index, 0)
        self.assertEqual(score.hit_id, "test_id")
        self.assertEqual(score.eval_score, 4)
        self.assertTrue(score.relevant)
        self.assertEqual(score.justification, "Test justification")
    
    def test_eval_result(self):
        """Test the EvalResult model."""
        query = Query(text="test query")
        metrics = {"ndcg": 0.8, "map": 0.7, "mrr": 0.9}
        
        hit_scores = [
            EvalScore(index=0, hit_id="hit1", eval_score=4, relevant=True),
            EvalScore(index=1, hit_id="hit2", eval_score=2, relevant=False)
        ]
        
        usage = {"evaluation_input_tokens": 100}
        
        result = EvalResult(
            query=query,
            metrics=metrics,
            hit_scores=hit_scores,
            usage=usage
        )
        
        self.assertEqual(result.query, query)
        self.assertEqual(result.metrics, metrics)
        self.assertEqual(len(result.hit_scores), 2)
        self.assertEqual(result.usage, usage)


if __name__ == "__main__":
    unittest.main()