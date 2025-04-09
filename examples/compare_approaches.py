#!/usr/bin/env python3
"""
Example of comparing different search approaches using Pinecone Evals.

This script shows how to:
1. Compare three search strategies (basic search and two reranking methods)
2. Evaluate them against test queries
3. Generate a visual HTML report of the results
"""
import os

from pinecone import Pinecone

from pinecone_evals import PineconeEval, SearchEvaluator, Query, SearchHit, SearchResult

# Number of results to return per search
MAX_RESULTS = 10


def main():
    """Run search comparison evaluation and generate report."""
    # Get API key from environment (recommended) or use a placeholder
    api_key = os.environ.get("PINECONE_API_KEY", "your_api_key_here")

    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)
    index = pc.Index("wikipedia")
    
    # Initialize the evaluation system
    eval_client = PineconeEval(api_key=api_key)
    evaluator = SearchEvaluator(eval_client)

    # Define test queries
    test_queries = [
        Query(text="what is vector search?"),
        Query(text="explain semantic search"),
        Query(text="how to optimize query performance"),
    ]

    # Define our search functions
    # 1. Basic semantic search
    def run_basic_search(query):
        return semantic_search(index, query)
    
    # 2. Semantic search with Cohere reranking
    def run_cohere_search(query):
        return semantic_search_rerank(index, query, "cohere-rerank-3.5")
    
    # 3. Semantic search with BGE reranking
    def run_bge_search(query):
        return semantic_search_rerank(index, query, "bge-reranker-v2-m3")

    # Evaluate each approach
    print("Evaluating approaches...")
    evaluator.evaluate_approach(
        "basic_semantic_search", run_basic_search, test_queries, async_mode=True
    )
    
    evaluator.evaluate_approach(
        "cohere_reranking", run_cohere_search, test_queries, async_mode=True
    )
    
    evaluator.evaluate_approach(
        "bge_reranking", run_bge_search, test_queries, async_mode=True
    )
    
    # Generate HTML report with results
    print("Generating HTML report...")
    evaluator.generate_report("run_evals.html", "html")
    print("Report generated: run_evals.html")


def semantic_search(index, query: Query) -> SearchResult:
    results = index.search_records(
        namespace="default",
        query={
            "inputs": {"text": query.text},
            "top_k": MAX_RESULTS,
        },
    )
    hits = []
    for match in results["result"]["hits"]:
        hits.append(SearchHit(**match["fields"]))
    return SearchResult(query=query, hits=hits)


def semantic_search_rerank(index, query: Query, model: str) -> SearchResult:
    results = index.search_records(
        namespace="default",
        query={
            "inputs": {"text": query.text},
            "top_k": 100,
        },
        rerank={
            "model": model,
            "rank_fields": ["text"],
            "top_n": MAX_RESULTS,
        },
    )
    hits = []
    for match in results["result"]["hits"]:
        hits.append(SearchHit(**match["fields"]))
    return SearchResult(query=query, hits=hits)


if __name__ == "__main__":
    main()
