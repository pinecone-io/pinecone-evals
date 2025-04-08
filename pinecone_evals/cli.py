"""Command-line interface for Pinecone Evals."""

import argparse
import json
import sys
from typing import Dict, Any, List, Optional

from .client import PineconeEval
from .models import Query, SearchHit, SearchResult
from .evaluator import SearchEvaluator


def load_queries_from_file(filepath: str) -> List[Query]:
    """Load test queries from a JSON file."""
    with open(filepath, "r") as f:
        query_data = json.load(f)

    return [Query(text=q["text"]) for q in query_data]


def load_hits_from_file(filepath: str) -> Dict[str, List[SearchHit]]:
    """Load search hits from a JSON file."""
    with open(filepath, "r") as f:
        hits_data = json.load(f)

    result = {}
    for query_id, hits in hits_data.items():
        result[query_id] = [SearchHit(id=hit["id"], text=hit["text"]) for hit in hits]

    return result


def run_evaluation(
    api_key: str,
    queries_file: str,
    hits_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Run an evaluation from the command line."""
    # Initialize the client
    client = PineconeEval(api_key=api_key)
    evaluator = SearchEvaluator(client)

    # Load data
    queries = load_queries_from_file(queries_file)
    hits_by_query = load_hits_from_file(hits_file)

    # Define a search function that uses the preloaded hits
    def fixed_search(query: Query) -> SearchResult:
        query_id = query.text
        if query_id not in hits_by_query:
            print(f"Warning: No hits found for query: {query_id}")
            return SearchResult(query=query, hits=[])
        return SearchResult(query=query, hits=hits_by_query[query_id])

    # Run evaluation
    results = evaluator.evaluate_approach("api_evaluation", fixed_search, queries)

    # Generate report
    if verbose:
        report = evaluator.generate_report()
        print(report)

    # Save results
    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

    return results


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Pinecone Evals CLI")
    parser.add_argument("--api-key", required=True, help="Pinecone API key")
    parser.add_argument("--queries", required=True, help="Path to queries JSON file")
    parser.add_argument("--hits", required=True, help="Path to hits JSON file")
    parser.add_argument("--output", help="Path to output JSON file")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output")

    args = parser.parse_args()

    run_evaluation(
        api_key=args.api_key,
        queries_file=args.queries,
        hits_file=args.hits,
        output_file=args.output,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
