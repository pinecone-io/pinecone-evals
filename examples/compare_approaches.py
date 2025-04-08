#!/usr/bin/env python3
"""
Example of comparing different search approaches using Pinecone Evals.
"""

import os
import json
from pinecone_evals import PineconeEval, SearchEvaluator, Query, SearchHit, SearchResult


def main():
    # Get API key from environment (recommended) or use a placeholder
    api_key = os.environ.get("PINECONE_API_KEY", "your_api_key_here")

    # Initialize the eval client
    eval_client = PineconeEval(api_key=api_key)

    # Create an evaluator
    evaluator = SearchEvaluator(eval_client)

    # Define some test queries
    test_queries = [
        Query(text="what is vector search?"),
        Query(text="explain semantic search"),
        Query(text="how to optimize query performance"),
    ]

    # Define search functions for different approaches

    def keyword_search(query: Query) -> SearchResult:
        """Simple keyword-based search."""
        # In a real application, this would call your keyword search system
        hits = []

        # Simple keyword matching logic (for demonstration)
        if "vector" in query.text.lower():
            hits = [
                SearchHit(
                    id="vs1",
                    text="Vector search uses vector representations to find similar items.",
                ),
                SearchHit(
                    id="vs2",
                    text="Traditional search uses keywords, while vector search uses embeddings.",
                ),
                SearchHit(
                    id="vs3",
                    text="Indexing is a crucial part of efficient vector search algorithms.",
                ),
            ]
        elif "semantic" in query.text.lower():
            hits = [
                SearchHit(
                    id="ss1",
                    text="Semantic search understands the intent behind search queries.",
                ),
                SearchHit(
                    id="ss2",
                    text="Vector databases are optimized for semantic search operations.",
                ),
                SearchHit(
                    id="ss3",
                    text="Embeddings capture the semantic meaning of text or images.",
                ),
            ]
        else:
            hits = [
                SearchHit(
                    id="perf1",
                    text="Query optimization techniques include caching and indexing.",
                ),
                SearchHit(
                    id="perf2",
                    text="Performance can be improved by using specialized vector indexes.",
                ),
                SearchHit(
                    id="perf3",
                    text="Benchmarking is essential for measuring query performance.",
                ),
            ]

        return SearchResult(query=query, hits=hits)

    def hybrid_search(query: Query) -> SearchResult:
        """Hybrid search combining keyword and semantic approaches."""
        # Get base results from keyword search
        base_result = keyword_search(query)

        # Then add some additional context-aware results
        # In a real implementation, this would use a semantic search system
        additional_hits = []

        if "vector" in query.text.lower() or "semantic" in query.text.lower():
            additional_hits = [
                SearchHit(
                    id="h1",
                    text="Hybrid search combines keyword matching with semantic understanding.",
                ),
                SearchHit(
                    id="h2",
                    text="Embedding models transform queries into high-dimensional vectors.",
                ),
            ]
        else:
            additional_hits = [
                SearchHit(
                    id="h3",
                    text="Query planning is important for complex search operations.",
                ),
                SearchHit(
                    id="h4",
                    text="Vector similarity metrics include cosine similarity and dot product.",
                ),
            ]

        # Combine and prioritize results (simple approach for demo)
        # In a real implementation, this would use a reranking model
        all_hits = base_result.hits + additional_hits
        reranked_hits = sorted(
            all_hits,
            key=lambda hit: sum(
                w in hit.text.lower() for w in query.text.lower().split()
            ),
            reverse=True,
        )

        return SearchResult(query=query, hits=reranked_hits[:4])  # Limit to top 4

    # Evaluate each approach
    print("Evaluating keyword search...")
    evaluator.evaluate_approach("keyword_search", keyword_search, test_queries)

    print("Evaluating hybrid search...")
    evaluator.evaluate_approach("hybrid_search", hybrid_search, test_queries)

    # Compare approaches
    comparison = evaluator.compare_approaches()
    print("\nComparison Results:")
    print(json.dumps(comparison, indent=2))

    # Generate report
    report = evaluator.generate_report("comparison_report.md")
    print(f"\nReport generated and saved to comparison_report.md")


if __name__ == "__main__":
    main()
