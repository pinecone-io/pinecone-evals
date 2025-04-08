#!/usr/bin/env python3
"""
Basic example of using the Pinecone Evals library.
"""

import os
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
        Query(text="what is machine learning?"),
        Query(text="how do databases work?"),
        Query(text="best programming languages"),
    ]

    # Define a simple search function
    def basic_search(query: Query) -> SearchResult:
        """Simple search function that returns mock results."""
        # In a real application, this would call your actual search system
        if "machine learning" in query.text.lower():
            hits = [
                SearchHit(
                    id="ml1",
                    text="Machine learning is a branch of artificial intelligence focused on building systems that learn from data.",
                ),
                SearchHit(
                    id="ml2",
                    text="Deep learning is a subset of machine learning that uses neural networks with many layers.",
                ),
                SearchHit(
                    id="ml3", text="Supervised learning requires labeled training data."
                ),
            ]
        elif "database" in query.text.lower():
            hits = [
                SearchHit(
                    id="db1",
                    text="Databases store and organize data for easy retrieval and management.",
                ),
                SearchHit(
                    id="db2",
                    text="SQL is a language used to query relational databases.",
                ),
                SearchHit(
                    id="db3",
                    text="NoSQL databases provide flexible schema design for unstructured data.",
                ),
            ]
        else:
            hits = [
                SearchHit(
                    id="prog1",
                    text="Python is a popular language for data science and machine learning.",
                ),
                SearchHit(
                    id="prog2",
                    text="JavaScript is used for web development on both client and server sides.",
                ),
                SearchHit(
                    id="prog3",
                    text="Rust provides memory safety without garbage collection.",
                ),
            ]

        return SearchResult(query=query, hits=hits)

    # Evaluate the search approach
    results = evaluator.evaluate_approach(
        name="basic_search", search_fn=basic_search, queries=test_queries
    )

    # Print the evaluation metrics
    print("Evaluation Metrics:")
    for metric_name, metric_values in results["metrics"].items():
        print(f"  {metric_name}: {metric_values['mean']:.4f}")

    # Generate a report
    report = evaluator.generate_report("basic_evaluation_report.md")
    print(f"\nReport generated and saved to basic_evaluation_report.md")


if __name__ == "__main__":
    main()
