"""Utilities for evaluating and comparing search approaches."""

import statistics
from typing import Dict, List, Any, Optional, Callable

from .models import Query, SearchResult, EvalResult
from .client import PineconeEval


class SearchEvaluator:
    """Utility for evaluating and comparing search approaches."""

    def __init__(self, eval_client: PineconeEval):
        self.eval_client = eval_client
        self.results = {}  # Store results by approach name

    def evaluate_approach(self,
                          name: str,
                          search_fn: Callable[[Query], SearchResult],
                          queries: List[Query]) -> Dict[str, Any]:
        """
        Evaluate a search approach on a set of queries.

        Args:
            name: Name to identify this approach
            search_fn: Function that takes a Query and returns SearchResult
            queries: List of queries to evaluate

        Returns:
            Dictionary with evaluation metrics
        """
        approach_results = []

        for query in queries:
            # Execute the search
            search_result = search_fn(query)

            # Evaluate the search result
            eval_result = self.eval_client.evaluate_search(
                query=query,
                hits=search_result.hits
            )

            approach_results.append(eval_result)

        # Aggregate metrics across all queries
        aggregated_metrics = self._aggregate_metrics(approach_results)

        # Store results for later comparison
        self.results[name] = {
            "metrics": aggregated_metrics,
            "detailed_results": approach_results
        }

        return self.results[name]

    def _aggregate_metrics(self, eval_results: List[EvalResult]) -> Dict[str, Dict[str, float]]:
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
                "stddev": statistics.stdev(metric_values) if len(metric_values) > 1 else 0
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
                    key=lambda approach: self.results[approach]["metrics"][metric]["mean"]
                ),
                "values": {
                    approach: results["metrics"][metric]["mean"]
                    for approach, results in self.results.items()
                }
            }

        return comparison

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a report of the evaluation results."""
        if not self.results:
            return "No approaches have been evaluated"

        comparison = self.compare_approaches()

        report = []
        report.append("# Search Evaluation Report")
        report.append("\n## Comparison Summary\n")

        # Create a table of results
        approaches = list(self.results.keys())
        metrics = list(next(iter(self.results.values()))["metrics"].keys())

        # Table header
        report.append("| Metric | " + " | ".join(approaches) + " | Best Approach |")
        report.append("|--------|" + "|".join(["---------" for _ in approaches]) + "|-------------|")

        # Table rows
        for metric in metrics:
            values = [f"{self.results[approach]['metrics'][metric]['mean']:.4f}" for approach in approaches]
            best = comparison[metric]["best_approach"]
            report.append(f"| {metric} | " + " | ".join(values) + f" | **{best}** |")
        
        # Add detailed per-approach results
        report.append("\n## Detailed Results\n")
        
        for approach_name, approach_data in self.results.items():
            report.append(f"### {approach_name}\n")
            
            # Per-metric detailed stats
            report.append("| Metric | Mean | Median | Min | Max | StdDev |")
            report.append("|--------|------|--------|-----|-----|--------|")
            
            for metric, stats in approach_data["metrics"].items():
                report.append(f"| {metric} | {stats['mean']:.4f} | {stats['median']:.4f} | {stats['min']:.4f} | {stats['max']:.4f} | {stats['stddev']:.4f} |")
            
            # Add per-query results if available
            if "detailed_results" in approach_data:
                report.append("\n#### Per-Query Results\n")
                report.append("| Query | NDCG | MAP | MRR | Relevant Hits |")
                report.append("|-------|------|-----|-----|---------------|")
                
                for result in approach_data["detailed_results"]:
                    query_text = result.query.text[:30] + "..." if len(result.query.text) > 30 else result.query.text
                    relevant_hits = sum(1 for score in result.hit_scores if score.relevant)
                    total_hits = len(result.hit_scores)
                    
                    report.append(f"| \"{query_text}\" | {result.metrics.get('ndcg', 0):.4f} | {result.metrics.get('map', 0):.4f} | {result.metrics.get('mrr', 0):.4f} | {relevant_hits}/{total_hits} |")
            
            report.append("\n")

        report_text = "\n".join(report)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)

        return report_text