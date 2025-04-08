#!/usr/bin/env python3
"""
Example demonstrating direct API usage with the Pinecone Evals client.
"""

import os
import json
from pinecone_evals import PineconeEval, Query, SearchHit


def main():
    # Get API key from environment (recommended) or use a placeholder
    api_key = os.environ.get("PINECONE_API_KEY", "your_api_key_here")

    # Initialize the eval client
    eval_client = PineconeEval(api_key=api_key)

    # Create a test query and hits
    query = Query(text="What are the benefits of renewable energy?")

    hits = [
        SearchHit(
            id="doc1",
            text="Renewable energy provides sustainable power, reduces greenhouse gas emissions, and helps mitigate climate change by leveraging natural resources.",
        ),
        SearchHit(
            id="doc2",
            text="Renewable energy is seen as an alternative to fossil fuels and can be crucial in reducing carbon footprints, though its implementation might face technical challenges.",
        ),
        SearchHit(
            id="doc3",
            text="The deployment of smart grids is modernizing urban power distribution, leading to more efficient energy management.",
        ),
        SearchHit(
            id="doc4",
            text="Blockchain technology offers decentralized financial solutions.",
        ),
    ]

    # Evaluate the hits for the query
    print("Evaluating search results...")
    result = eval_client.evaluate_search(query=query, hits=hits, debug=True)

    # Print the evaluation results
    print("\nEvaluation Results:")
    print(f"Query: {result.query.text}")
    print("\nMetrics:")
    for metric_name, metric_value in result.metrics.items():
        print(f"  {metric_name}: {metric_value:.4f}")

    print("\nHit Scores:")
    for score in result.hit_scores:
        relevance = "Relevant" if score.relevant else "Not relevant"
        print(
            f"  Hit {score.index} (ID: {score.hit_id}): Score {score.eval_score}/4 - {relevance}"
        )
        if score.justification:
            print(f"    Justification: {score.justification[:100]}...")

    print("\nToken Usage:")
    for usage_type, token_count in result.usage.items():
        print(f"  {usage_type}: {token_count}")


if __name__ == "__main__":
    main()
