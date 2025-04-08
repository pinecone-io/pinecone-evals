#!/usr/bin/env python3
"""
Example usage of the Pinecone Evals library.
"""

import json
import os
from pinecone_evals import (
    Query, 
    SearchResult
)


def main():
    """Example usage of the Pinecone Evals library."""
    # Initialize the eval client (using mock implementation for demonstration)
    # In production, use: PineconeEval(api_key="your_api_key_here")
    from pinecone_evals import MockPineconeEval
    eval_client = MockPineconeEval()
    
    # Create an evaluator
    from pinecone_evals import SearchEvaluator
    evaluator = SearchEvaluator(eval_client)

    # Define some test queries
    test_queries = [
        Query(text="what is the capital of france?"),
        Query(text="how do neural networks work?"),
        Query(text="best practices for vector search")
    ]

    # Define search functions for different approaches
    def basic_search(query: Query) -> SearchResult:
        # This would normally call your search API
        # Mocking for demonstration
        if "capital" in query.text:
            hits = [
                {"id": "doc1", "text": "Paris is the capital and largest city of France."},
                {"id": "doc2", "text": "France is a country in Western Europe."},
                {"id": "doc3", "text": "The Eiffel Tower is in Paris, France."}
            ]
        else:
            hits = [
                {"id": "doc4", "text": "Vector search is a technique for finding similar vectors."},
                {"id": "doc5", "text": "Neural networks are composed of interconnected layers of neurons."},
                {"id": "doc6", "text": "Machine learning algorithms learn patterns from data."}
            ]
        return SearchResult(query=query, hits=hits)

    def reranked_search(query: Query) -> SearchResult:
        # Get base results then apply reranking
        base_result = basic_search(query)

        # This would normally apply a reranking model
        # Mocking improved ordering for demonstration - simple word matching
        query_words = query.text.lower().split()
        
        # Count matching words for each hit
        def count_matches(hit):
            text = hit["text"].lower()
            return sum(word in text for word in query_words)
        
        # Sort hits by match count (descending)
        reranked_hits = sorted(base_result.hits, key=count_matches, reverse=True)
        return SearchResult(query=query, hits=reranked_hits)
    
    # Demonstrate with custom fields
    def enhanced_search(query: Query) -> SearchResult:
        # This would normally call your search API with additional fields
        # Mocking for demonstration
        if "capital" in query.text:
            hits = [
                {
                    "id": "doc1", 
                    "text": "Paris is the capital of France.",
                    "title": "Capital Cities",
                    "metadata": {"population": "2.2 million", "country": "France"}
                },
                {
                    "id": "doc2", 
                    "text": "France has many beautiful cities.",
                    "title": "European Countries",
                    "metadata": {"continent": "Europe", "eu_member": True}
                }
            ]
        else:
            hits = [
                {
                    "id": "doc4", 
                    "text": "Vector search finds similar items.",
                    "title": "Search Technology",
                    "code_snippet": "index.query(vectors=[query_vector], top_k=10)"
                },
                {
                    "id": "doc5", 
                    "text": "Neural networks process data in layers.",
                    "title": "Machine Learning",
                    "diagram": "Input Layer → Hidden Layers → Output Layer"
                }
            ]
        return SearchResult(query=query, hits=hits)

    # Evaluate each approach
    print("Evaluating basic search...")
    evaluator.evaluate_approach("basic_search", basic_search, test_queries)
    
    print("Evaluating reranked search...")
    evaluator.evaluate_approach("reranked_search", reranked_search, test_queries)
    
    print("Evaluating enhanced search with custom fields...")
    evaluator.evaluate_approach("enhanced_search", enhanced_search, test_queries)

    # Compare approaches
    print("\nComparing approaches...")
    comparison = evaluator.compare_approaches()
    print(json.dumps(comparison, indent=2))

    # Generate reports in both formats
    md_report = evaluator.generate_report("search_eval_report.md", format="md")
    html_report = evaluator.generate_report("search_eval_report.html", format="html")
    
    print("\nReports generated and saved to:")
    print("- search_eval_report.md (Markdown format)")
    print("- search_eval_report.html (Interactive HTML format with visualizations)")
    print("\nOpen the HTML report in your browser for an interactive experience with:")
    print("- Visual performance charts")
    print("- Search result details with justifications")
    print("- Interactive query exploration")


if __name__ == "__main__":
    main()