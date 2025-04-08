"""Utility functions for working with Pinecone Evals."""

import json
import os
from typing import Dict, Any, List, Optional, Union

from .models import EvalResult
from .client import PineconeEval
from .mock import MockPineconeEval


def get_eval_client(api_key: Optional[str] = None, 
                   use_mock: bool = False,
                   endpoint: str = "https://api.pinecone.io/eval") -> Union[PineconeEval, MockPineconeEval]:
    """
    Get an evaluation client, either real or mock.
    
    Args:
        api_key: Pinecone API key. If None and use_mock=False, will try to get
                from PINECONE_API_KEY environment variable.
        use_mock: If True, returns a mock client instead of a real one.
        endpoint: API endpoint for the real client (ignored if use_mock=True).
        
    Returns:
        A PineconeEval client or MockPineconeEval client.
        
    Raises:
        ValueError: If api_key is not provided and not found in environment.
    """
    if use_mock:
        return MockPineconeEval()
    
    # Try to get API key from environment if not provided
    if api_key is None:
        api_key = os.environ.get("PINECONE_API_KEY")
        
    if not api_key:
        raise ValueError(
            "API key is required for real API calls. "
            "Either provide api_key parameter or set PINECONE_API_KEY environment variable. "
            "Alternatively, use use_mock=True for development."
        )
    
    return PineconeEval(api_key=api_key, endpoint=endpoint)


def format_metrics_table(metrics: Dict[str, Dict[str, float]]) -> str:
    """
    Format metrics as a markdown table.
    
    Args:
        metrics: Dictionary of metric names to values
        
    Returns:
        Formatted markdown table string
    """
    # Table header
    rows = ["| Metric | Mean | Median | Min | Max | StdDev |",
            "|--------|------|--------|-----|-----|--------|"]
    
    # Add rows for each metric
    for metric_name, values in metrics.items():
        row = (f"| {metric_name} | "
               f"{values['mean']:.4f} | "
               f"{values['median']:.4f} | "
               f"{values['min']:.4f} | "
               f"{values['max']:.4f} | "
               f"{values['stddev']:.4f} |")
        rows.append(row)
    
    return "\n".join(rows)


def save_results(results: Dict[str, Any], filepath: str) -> None:
    """
    Save evaluation results to a JSON file.
    
    Args:
        results: Dictionary containing evaluation results
        filepath: Path to save the results file
    """
    # Convert EvalResult objects to dictionaries
    serializable_results = {}
    
    for approach, approach_data in results.items():
        metrics = approach_data["metrics"]
        detailed_results = []
        
        for result in approach_data.get("detailed_results", []):
            if isinstance(result, EvalResult):
                detailed_results.append({
                    "query": result.query.text,
                    "metrics": result.metrics,
                    "usage": result.usage,
                    "hit_scores": [
                        {
                            "index": score.index,
                            "hit_id": score.hit_id,
                            "eval_score": score.eval_score,
                            "relevant": score.relevant,
                            "justification": score.justification
                        }
                        for score in result.hit_scores
                    ]
                })
        
        serializable_results[approach] = {
            "metrics": metrics,
            "detailed_results": detailed_results
        }
    
    with open(filepath, "w") as f:
        json.dump(serializable_results, f, indent=2)


def load_results(filepath: str) -> Dict[str, Any]:
    """
    Load evaluation results from a JSON file.
    
    Args:
        filepath: Path to the results file
        
    Returns:
        Dictionary containing evaluation results
    """
    with open(filepath, "r") as f:
        return json.load(f)