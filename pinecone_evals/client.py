"""Client for interacting with the Pinecone Evals API."""

import requests
from typing import Dict, List, Any, Optional

from .models import Query, SearchHit, EvalPassage, EvalSearch


class PineconeEval:
    """Client for the Pinecone Evals API."""

    def __init__(self, api_key: str, endpoint: str = "https://api.pinecone.io/evals"):
        """
        Initialize the Pinecone Evals client.
        
        Args:
            api_key: Pinecone API key for authentication
            endpoint: API endpoint URL
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Api-Key": api_key
        })

    def evaluate_search(self,
                        query: Query,
                        hits: List[SearchHit],
                        fields: Optional[List[str]] = None,
                        debug: bool = True) -> EvalSearch:
        """
        Evaluate the relevance of search results for a given query.

        Args:
            query: The search query
            hits: List of search hits to evaluate
            fields: Fields to consider in evaluation
            debug: Enable detailed evaluation debugging

        Returns:
            EvalResult containing metrics and per-hit scores
        """
        if fields is None:
            fields = ["text"]
        
        request_data = {
            "query": {
                "inputs": {
                    "text": query.text
                }
            },
            "eval": {
                "fields": fields,
                "debug": debug
            },
            "hits": hits  # SearchHit is now a dict, so we can pass it directly
        }

        response = self._make_api_call(request_data)
        return self._parse_response(query, response, fields)

    def _make_api_call(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a call to the Pinecone Evals API.
        
        Args:
            request_data: The API request data
            
        Returns:
            API response data
            
        Raises:
            requests.HTTPError: If the API call fails
        """
        response = self.session.post(self.endpoint, json=request_data)
        response.raise_for_status()
        return response.json()

    def _parse_response(self, query: Query, response: Dict[str, Any], fields) -> EvalSearch:
        """
        Parse the API response into an EvalResult.
        
        Args:
            query: The original query
            response: The API response data
            
        Returns:
            Parsed EvalResult
        """
        hit_scores = []
        for hit_eval in response["hits"]:
            # Get the hit_id from fields (which might be nested differently in different responses)
            hit_id = hit_eval.get("id", "")
            if not hit_id and "fields" in hit_eval:
                hit_id = hit_eval["fields"].get("id", f"hit-{hit_eval['index']}")
            
            hit_scores.append(
                EvalPassage(
                    index=hit_eval["index"],
                    hit_id=hit_id,
                    fields=hit_eval["fields"],
                    eval_text=hit_eval["fields"][fields[0]],
                    eval_score=hit_eval.get("score", -1),  # Should be a value between 1-4
                    relevant=hit_eval["relevant"],
                    justification=hit_eval.get("justification")
                )
            )

        return EvalSearch(
            query=query,
            metrics=response["metrics"],
            hit_scores=hit_scores,
            usage=response["usage"]
        )