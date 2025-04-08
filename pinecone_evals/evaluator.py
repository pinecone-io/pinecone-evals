"""Utilities for evaluating and comparing search approaches."""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Union

from tqdm import tqdm

from .client import PineconeEval
from .models import EvalSearch, Query, SearchResult
from .reports import generate_markdown_report, generate_html_report


class SearchEvaluator:
    """Utility for evaluating and comparing search approaches."""

    def __init__(self, eval_client: PineconeEval):
        self.eval_client = eval_client
        self.results = {}  # Store results by approach name
        self.query_set = None  # Will be set when queries are first provided

    def evaluate_approach(
            self,
            name: str,
            search_fn: Callable[[Query], SearchResult],
            queries: Union[List[Query]],
            show_progress: bool = True,
            async_mode: bool = False,
            max_workers: int = 4,
            request_delay: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Evaluate a search approach on a set of queries.

        Args:
            name: Name to identify this approach
            search_fn: Function that takes a Query and returns SearchResult
            queries: List of queries or QuerySet to evaluate
            show_progress: Whether to show a progress bar during evaluation
            async_mode: Whether to process queries in parallel
            max_workers: Maximum number of parallel workers when async_mode is True
            request_delay: Delay between requests to respect rate limits (in seconds)

        Returns:
            Dictionary with evaluation metrics
        """

        # Use the queries from the QuerySet to ensure consistent IDs
        query_list = queries
        approach_results = []

        # Define function to process a single query
        def process_query(query):
            try:
                # Add delay between requests to respect rate limits
                time.sleep(request_delay)
                # Execute the search
                search_result = search_fn(query)
                # Evaluate the search result
                eval_result = self.eval_client.evaluate_search(
                    query=query, hits=search_result.hits
                )
                return eval_result
            except Exception as e:
                return {"error": str(e), "query": query.text, "query_id": query.id}

        # Process queries based on mode (async or sequential)
        if async_mode:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(process_query, query) for query in query_list]

                if show_progress:
                    with tqdm(
                            total=len(query_list),
                            desc=f"Evaluating '{name}'",
                            unit="query",
                            ncols=80,
                    ) as pbar:
                        for future in as_completed(futures):
                            result = future.result()
                            if isinstance(result, dict) and "error" in result:
                                print(
                                    f"Error processing query '{result['query']}' (ID: {result.get('query_id', 'unknown')}): {result['error']}"
                                )
                                continue
                            approach_results.append(result)
                            pbar.update(1)
                else:
                    for future in as_completed(futures):
                        result = future.result()
                        if isinstance(result, dict) and "error" in result:
                            print(
                                f"Error processing query '{result['query']}' (ID: {result.get('query_id', 'unknown')}): {result['error']}"
                            )
                            continue
                        approach_results.append(result)
        else:
            # Sequential processing
            iterator = (
                tqdm(query_list, desc=f"Evaluating '{name}'", unit="query", ncols=80)
                if show_progress
                else query_list
            )
            for query in iterator:
                # Execute the search
                try:
                    search_result = search_fn(query)
                    # Evaluate the search result
                    eval_result = self.eval_client.evaluate_search(
                        query=query, hits=search_result.hits
                    )
                    approach_results.append(eval_result)
                except Exception as e:
                    print(f"Error processing query '{query.text}' (ID: {query.id or 'unknown'}): {str(e)}")

        # Aggregate metrics across all queries
        aggregated_metrics = self._aggregate_metrics(approach_results)

        # Store results for later comparison
        self.results[name] = {
            "metrics": aggregated_metrics,
            "detailed_results": approach_results,
        }

        return self.results[name]

    def _aggregate_metrics(
            self, eval_results: List[EvalSearch]
    ) -> Dict[str, Dict[str, float]]:
        """Aggregate metrics across multiple query results."""
        all_metrics = {}

        # Extract each metric type
        for metric_name in eval_results[0].metrics.keys():
            metric_values = [result.metrics[metric_name] for result in eval_results]
            all_metrics[metric_name] = {
                "mean": statistics.mean(metric_values),
                "median": statistics.median(metric_values),
                "min": min(metric_values),
                "max": max(metric_values),
                "stddev": statistics.stdev(metric_values)
                if len(metric_values) > 1
                else 0,
            }

        return all_metrics

    def compare_approaches(self) -> Dict[str, Any]:
        """Compare the performance of all evaluated approaches."""
        if not self.results:
            return {"error": "No approaches have been evaluated"}

        comparison = {}

        # For each metric, identify the best approach
        metric_names = next(iter(self.results.values()))["metrics"].keys()

        for metric in metric_names:
            comparison[metric] = {
                "best_approach": max(
                    self.results.keys(),
                    key=lambda approach: self.results[approach]["metrics"][metric][
                        "mean"
                    ],
                ),
                "values": {
                    approach: results["metrics"][metric]["mean"]
                    for approach, results in self.results.items()
                },
            }

        return comparison

    def generate_report(
            self, output_file: Optional[str] = None, format: str = "md"
    ) -> str:
        """
        Generate a report of the evaluation results.

        Args:
            output_file: Optional file path to write the report to
            format: Report format, either 'md' (Markdown) or 'html' (HTML)

        Returns:
            The generated report as a string
        """
        if not self.results:
            return "No approaches have been evaluated"

        comparison = self.compare_approaches()

        if format.lower() == "html":
            return generate_html_report(self.results, comparison, output_file)
        else:
            return generate_markdown_report(self.results, comparison, output_file)
