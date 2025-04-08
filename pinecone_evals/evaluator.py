"""Utilities for evaluating and comparing search approaches."""

import statistics
from typing import Any, Callable, Dict, List, Optional

from .client import PineconeEval
from .models import EvalSearch, Query, SearchResult


class SearchEvaluator:
    """Utility for evaluating and comparing search approaches."""

    def __init__(self, eval_client: PineconeEval):
        self.eval_client = eval_client
        self.results = {}  # Store results by approach name

    def evaluate_approach(
        self,
        name: str,
        search_fn: Callable[[Query], SearchResult],
        queries: List[Query],
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate a search approach on a set of queries.

        Args:
            name: Name to identify this approach
            search_fn: Function that takes a Query and returns SearchResult
            queries: List of queries to evaluate
            show_progress: Whether to show a progress bar during evaluation

        Returns:
            Dictionary with evaluation metrics
        """
        approach_results = []

        # Setup progress tracking
        if show_progress:
            from tqdm import tqdm

            query_iterator = tqdm(
                queries, desc=f"Evaluating '{name}'", unit="query", ncols=80
            )
        else:
            query_iterator = queries

        # Process each query
        for query in query_iterator:
            # Execute the search
            search_result = search_fn(query)

            # Evaluate the search result
            eval_result = self.eval_client.evaluate_search(
                query=query, hits=search_result.hits
            )

            approach_results.append(eval_result)

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
                "stddev": statistics.stdev(metric_values) if len(metric_values) > 1 else 0,
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
        """Generate a report of the evaluation results.

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
            return self._generate_html_report(output_file, comparison)
        else:
            return self._generate_markdown_report(output_file, comparison)

    def _generate_markdown_report(
        self, output_file: Optional[str], comparison: Dict[str, Any]
    ) -> str:
        """Generate a Markdown report of the evaluation results."""
        report = []
        report.append("# Search Evaluation Report")
        report.append("\n## Comparison Summary\n")

        # Create a table of results
        approaches = list(self.results.keys())
        metrics = list(next(iter(self.results.values()))["metrics"].keys())

        # Table header
        report.append("| Metric | " + " | ".join(approaches) + " | Best Approach |")
        report.append(
            "|--------|" + "|".join(["---------" for _ in approaches]) + "|-------------|"
        )

        # Table rows
        for metric in metrics:
            values = [
                f"{self.results[approach]['metrics'][metric]['mean']:.4f}"
                for approach in approaches
            ]
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
                report.append(
                    f"| {metric} | {stats['mean']:.4f} | {stats['median']:.4f} | {stats['min']:.4f} | {stats['max']:.4f} | {stats['stddev']:.4f} |"
                )

            # Add per-query results if available
            if "detailed_results" in approach_data:
                report.append("\n#### Per-Query Results\n")
                report.append("| Query | NDCG | MAP | MRR | Relevant Hits |")
                report.append("|-------|------|-----|-----|---------------|")

                for result in approach_data["detailed_results"]:
                    query_text = (
                        result.query.text[:30] + "..."
                        if len(result.query.text) > 30
                        else result.query.text
                    )
                    relevant_hits = sum(
                        1 for score in result.hit_scores if score.relevant
                    )
                    total_hits = len(result.hit_scores)

                    report.append(
                        f'| "{query_text}" | {result.metrics.get("ndcg", 0):.4f} | {result.metrics.get("map", 0):.4f} | {result.metrics.get("mrr", 0):.4f} | {relevant_hits}/{total_hits} |'
                    )

            report.append("\n")

        # Add a per-query comparison to show best approach for each query
        if len(self.results) > 1:
            report.append("## Best Approach Per Query\n")

            # Collect all unique queries from all approaches
            all_queries = {}

            for approach_name, approach_data in self.results.items():
                if "detailed_results" in approach_data:
                    for result in approach_data["detailed_results"]:
                        query_text = result.query.text
                        if query_text not in all_queries:
                            all_queries[query_text] = {}

                        # Store this approach's metrics for this query
                        all_queries[query_text][approach_name] = {
                            "ndcg": result.metrics.get("ndcg", 0),
                            "map": result.metrics.get("map", 0),
                            "mrr": result.metrics.get("mrr", 0),
                        }

            # Create a table showing best approach per query
            report.append("| Query | Best for NDCG | Best for MAP | Best for MRR |")
            report.append("|-------|--------------|-------------|-------------|")

            for query_text, approaches in all_queries.items():
                query_display = (
                    query_text[:30] + "..." if len(query_text) > 30 else query_text
                )

                # Find best approach for each metric
                best_ndcg = max(approaches.items(), key=lambda x: x[1]["ndcg"])
                best_map = max(approaches.items(), key=lambda x: x[1]["map"])
                best_mrr = max(approaches.items(), key=lambda x: x[1]["mrr"])

                best_ndcg_text = f"**{best_ndcg[0]}** ({best_ndcg[1]['ndcg']:.4f})"
                best_map_text = f"**{best_map[0]}** ({best_map[1]['map']:.4f})"
                best_mrr_text = f"**{best_mrr[0]}** ({best_mrr[1]['mrr']:.4f})"

                report.append(
                    f'| "{query_display}" | {best_ndcg_text} | {best_map_text} | {best_mrr_text} |'
                )

        report_text = "\n".join(report)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)

        return report_text

    def _generate_html_report(
        self, output_file: Optional[str], comparison: Dict[str, Any]
    ) -> str:
        """Generate an interactive HTML report of the evaluation results."""
        # Import utilities for HTML generation
        import json
        from html import escape

        approaches = list(self.results.keys())
        metrics = list(next(iter(self.results.values()))["metrics"].keys())

        # Create a structured HTML document
        html_parts = []
        
        # HTML header and styles
        html_parts.extend([
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            "    <title>Search Evaluation Report</title>",
            '    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
            '    <script src="https://cdn.tailwindcss.com"></script>',
            "    <style>",
            "        .tab-content { display: none; }",
            "        .tab-content.active { display: block; }",
            "        .approach-tab.active { background-color: #4F46E5; color: white; }",
            "        .hit { border: 1px solid #e5e7eb; padding: 8px; margin-bottom: 8px; border-radius: 4px; }",
            "        .hit.relevant { border-left: 4px solid #10B981; }",
            "        .hit.not-relevant { border-left: 4px solid #EF4444; }",
            "    </style>",
            "</head>",
            '<body class="bg-gray-50">',
            '    <div class="container mx-auto px-4 py-8">',
            '        <h1 class="text-3xl font-bold mb-8">Search Evaluation Report</h1>',
        ])
        
        # Executive summary section
        html_parts.extend([
            '        <div class="bg-white rounded-lg shadow p-6 mb-8">',
            '            <h2 class="text-xl font-semibold mb-4">Executive Summary</h2>',
            '            <div class="prose max-w-none">',
            f'                <p class="mb-2">This report compares {len(approaches)} search approaches: <strong>{", ".join(approaches)}</strong>.</p>',
            '                <div class="mt-4">',
            '                    <h3 class="text-lg font-semibold mb-2">Key Findings:</h3>',
            '                    <ul class="list-disc pl-5 space-y-2">',
        ])
        
        # Add a summary item for each metric
        for metric in metrics:
            best_approach = comparison[metric]["best_approach"]
            best_value = comparison[metric]["values"][best_approach]
            html_parts.append(
                f'                        <li><strong>{metric.upper()}</strong>: <span class="font-medium text-indigo-600">{best_approach}</span> performed best with a score of {best_value:.4f}</li>'
            )
            
            # Add performance differences if there are multiple approaches
            if len(approaches) > 1:
                # Calculate performance differences
                values = [self.results[approach]["metrics"][metric]["mean"] for approach in approaches]
                max_value = max(values)
                min_value = min(values)
                diff_percentage = ((max_value - min_value) / max_value * 100) if max_value > 0 else 0
                
                if diff_percentage > 10:  # Only highlight significant differences
                    html_parts.append(
                        f'                        <li class="pl-5 text-sm text-gray-600">Performance gap of <span class="font-medium">{diff_percentage:.1f}%</span> between best and worst approach</li>'
                    )
        
        html_parts.extend([
            '                    </ul>',
            '                </div>',
            '            </div>',
            '        </div>',
        ])
        
        # Charts section
        html_parts.extend([
            '        <div class="bg-white rounded-lg shadow p-6 mb-8">',
            '            <h2 class="text-xl font-semibold mb-4">Comparison Charts</h2>',
            '            <div class="flex flex-wrap">',
            '                <div class="w-full lg:w-1/3 p-4">',
            '                    <canvas id="ndcgChart"></canvas>',
            "                </div>",
            '                <div class="w-full lg:w-1/3 p-4">',
            '                    <canvas id="mapChart"></canvas>',
            "                </div>",
            '                <div class="w-full lg:w-1/3 p-4">',
            '                    <canvas id="mrrChart"></canvas>',
            "                </div>",
            "            </div>",
            "        </div>",
        ])
        
        # Approach tabs navigation
        html_parts.extend([
            '        <div class="bg-white rounded-lg shadow mb-8">',
            '            <div class="flex overflow-x-auto border-b">',
        ])
        
        # Add approach tabs
        for i, approach in enumerate(approaches):
            active_class = " active" if i == 0 else ""
            html_parts.append(
                f'                <button class="approach-tab px-6 py-3 font-medium{active_class}" onclick="showTab(\'{approach}\')">{escape(str(approach))}</button>'
            )
        
        html_parts.append("            </div>")
        
        # Add approach content sections
        html_parts.append('            <div class="p-6">')
        
        for i, approach_name in enumerate(approaches):
            approach_data = self.results[approach_name]
            active_class = " active" if i == 0 else ""
            
            html_parts.append(f'                <div id="{approach_name}-tab" class="tab-content{active_class}">')
            html_parts.append(f'                    <h3 class="text-lg font-semibold mb-4">{escape(str(approach_name))}</h3>')
            
            # Metrics table
            html_parts.extend([
                '                    <div class="overflow-x-auto mb-6">',
                '                        <table class="min-w-full divide-y divide-gray-200">',
                "                            <thead>",
                "                                <tr>",
                '                                    <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>',
                '                                    <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mean</th>',
                '                                    <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Median</th>',
                '                                    <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Min</th>',
                '                                    <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Max</th>',
                '                                    <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">StdDev</th>',
                "                                </tr>",
                "                            </thead>",
                '                            <tbody class="bg-white divide-y divide-gray-200">',
            ])
            
            for metric, stats in approach_data["metrics"].items():
                html_parts.extend([
                    "                                <tr>",
                    f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{escape(str(metric))}</td>',
                    f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["mean"]:.4f}</td>',
                    f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["median"]:.4f}</td>',
                    f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["min"]:.4f}</td>',
                    f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["max"]:.4f}</td>',
                    f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["stddev"]:.4f}</td>',
                    "                                </tr>",
                ])
            
            html_parts.extend([
                "                            </tbody>",
                "                        </table>",
                "                    </div>",
            ])
            
            # Per-query results with expandable details
            if "detailed_results" in approach_data:
                html_parts.extend([
                    '                    <h4 class="text-md font-semibold mb-2">Query Results</h4>',
                    '                    <div class="space-y-4">',
                ])
                
                for j, result in enumerate(approach_data["detailed_results"]):
                    query_id = f"{approach_name}-query-{j}"
                    html_parts.extend([
                        '                        <div class="border border-gray-200 rounded-md">',
                        f'                            <div class="flex justify-between items-center p-4 cursor-pointer" onclick="toggleQueryDetails(\'{query_id}\')">',
                        f'                                <div class="font-medium">"{escape(str(result.query.text))}"</div>',
                        '                                <div class="text-sm bg-blue-100 rounded px-2 py-1">',
                    ])
                    
                    relevant_hits = sum(1 for score in result.hit_scores if score.relevant)
                    total_hits = len(result.hit_scores)
                    html_parts.append(
                        f"                                    NDCG: {result.metrics.get('ndcg', 0):.4f} | MAP: {result.metrics.get('map', 0):.4f} | MRR: {result.metrics.get('mrr', 0):.4f} | Relevant: {relevant_hits}/{total_hits}"
                    )
                    
                    html_parts.extend([
                        "                                </div>",
                        "                            </div>",
                        f'                            <div id="{query_id}" class="hidden p-4 bg-gray-50 border-t">',
                        '                                <h5 class="font-medium mb-2">Search Results</h5>',
                        '                                <div class="space-y-2">',
                    ])
                    
                    # Show all hits with metadata and highlighting relevance
                    for k, hit_score in enumerate(result.hit_scores):
                        justification = hit_score.justification
                        relevant_class = "relevant" if hit_score.relevant else "not-relevant"
                        html_parts.extend([
                            f'                                    <div class="hit {relevant_class} p-3">',
                            '                                        <div class="flex justify-between items-center mb-2">',
                            f'                                            <span class="font-medium text-gray-800">Result #{k + 1} · ID: {escape(str(hit_score.hit_id))}</span>',
                            f'                                            <span class="text-sm px-2 py-1 rounded-full {" bg-green-100 text-green-800" if hit_score.relevant else " bg-red-100 text-red-800"}">',
                            f"                                                Score: {hit_score.eval_score}/4 · {'Relevant' if hit_score.relevant else 'Not Relevant'}",
                            "                                            </span>",
                            "                                        </div>",
                            
                            # Content with styled text
                            f'                                        <div class="mt-2 p-3 bg-white rounded border border-gray-200 text-gray-800">{escape(str(hit_score.eval_text))}</div>',
                            
                            # Justification with explanatory note
                            '                                        <div class="mt-2 text-sm">',
                            '                                            <span class="font-medium text-gray-700">Evaluation justification:</span>',
                            f'                                            <div class="mt-1 pl-3 border-l-2 border-gray-300 text-gray-600">{escape(str(justification))}</div>',
                            '                                        </div>',
                            "                                    </div>",
                        ])
                    
                    html_parts.extend([
                        "                                </div>",
                        "                            </div>",
                        "                        </div>",
                    ])
                
                html_parts.append("                    </div>")
            
            html_parts.append("                </div>")
        
        html_parts.extend([
            "            </div>",
            "        </div>",
        ])
        
        # Best approaches per query comparison
        if len(self.results) > 1:
            html_parts.extend([
                '        <div class="bg-white rounded-lg shadow p-6 mb-8">',
                '            <h2 class="text-xl font-semibold mb-4">Best Approach Per Query</h2>',
                '            <div class="overflow-x-auto">',
                '                <table class="min-w-full divide-y divide-gray-200">',
                "                    <thead>",
                "                        <tr>",
                '                            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Query</th>',
                '                            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best for NDCG</th>',
                '                            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best for MAP</th>',
                '                            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best for MRR</th>',
                "                        </tr>",
                "                    </thead>",
                '                    <tbody class="bg-white divide-y divide-gray-200">',
            ])
            
            # Collect all unique queries from all approaches
            all_queries = {}
            
            for approach_name, approach_data in self.results.items():
                if "detailed_results" in approach_data:
                    for result in approach_data["detailed_results"]:
                        query_text = result.query.text
                        if query_text not in all_queries:
                            all_queries[query_text] = {}
                        
                        # Store this approach's metrics for this query
                        all_queries[query_text][approach_name] = {
                            "ndcg": result.metrics.get("ndcg", 0),
                            "map": result.metrics.get("map", 0),
                            "mrr": result.metrics.get("mrr", 0),
                        }
            
            for query_text, approaches_metrics in all_queries.items():
                # Find best approach for each metric
                best_ndcg = max(approaches_metrics.items(), key=lambda x: x[1]["ndcg"])
                best_map = max(approaches_metrics.items(), key=lambda x: x[1]["map"])
                best_mrr = max(approaches_metrics.items(), key=lambda x: x[1]["mrr"])
                
                html_parts.extend([
                    "                        <tr>",
                    f'                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">"{escape(str(query_text))}"</td>',
                    f'                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="font-medium">{escape(str(best_ndcg[0]))}</span> ({best_ndcg[1]["ndcg"]:.4f})</td>',
                    f'                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="font-medium">{escape(str(best_map[0]))}</span> ({best_map[1]["map"]:.4f})</td>',
                    f'                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="font-medium">{escape(str(best_mrr[0]))}</span> ({best_mrr[1]["mrr"]:.4f})</td>',
                    "                        </tr>",
                ])
            
            html_parts.extend([
                "                    </tbody>",
                "                </table>",
                "            </div>",
                "        </div>",
            ])
        
        # Add JSON data for charts
        chart_data = {}
        for metric in metrics:
            chart_data[metric] = {
                "labels": approaches,
                "values": [self.results[approach]["metrics"][metric]["mean"] for approach in approaches]
            }
            
        html_parts.extend([
            "        <script>",
            f"            const chartData = {json.dumps(chart_data)};",
            "            ",
            "            // Tab switching functionality",
            "            function showTab(tabName) {",
            "                // Hide all tabs",
            "                document.querySelectorAll('.tab-content').forEach(tab => {",
            "                    tab.classList.remove('active');",
            "                });",
            "                ",
            "                // Show selected tab",
            "                document.getElementById(tabName + '-tab').classList.add('active');",
            "                ",
            "                // Update tab buttons",
            "                document.querySelectorAll('.approach-tab').forEach(btn => {",
            "                    btn.classList.remove('active');",
            "                });",
            "                ",
            "                // Highlight active button",
            "                document.querySelector(`[onclick=\"showTab('${tabName}')\"]`).classList.add('active');",
            "            }",
            "            ",
            "            // Toggle query details",
            "            function toggleQueryDetails(queryId) {",
            "                const detailsEl = document.getElementById(queryId);",
            "                detailsEl.classList.toggle('hidden');",
            "            }",
            "            ",
            "            // Init charts",
            "            document.addEventListener('DOMContentLoaded', function() {",
            "                // Create NDCG chart",
            "                new Chart(document.getElementById('ndcgChart'), {",
            "                    type: 'bar',",
            "                    data: {",
            "                        labels: chartData.ndcg.labels,",
            "                        datasets: [{",
            "                            label: 'NDCG Score',",
            "                            data: chartData.ndcg.values,",
            "                            backgroundColor: 'rgba(79, 70, 229, 0.6)',",
            "                            borderColor: 'rgb(79, 70, 229)',",
            "                            borderWidth: 1",
            "                        }]",
            "                    },",
            "                    options: {",
            "                        responsive: true,",
            "                        plugins: {",
            "                            title: {",
            "                                display: true,",
            "                                text: 'NDCG Performance'",
            "                            },",
            "                        },",
            "                        scales: {",
            "                            y: {",
            "                                beginAtZero: true,",
            "                                max: 1",
            "                            }",
            "                        }",
            "                    }",
            "                });",
            "                ",
            "                // Create MAP chart",
            "                new Chart(document.getElementById('mapChart'), {",
            "                    type: 'bar',",
            "                    data: {",
            "                        labels: chartData.map.labels,",
            "                        datasets: [{",
            "                            label: 'MAP Score',",
            "                            data: chartData.map.values,",
            "                            backgroundColor: 'rgba(16, 185, 129, 0.6)',",
            "                            borderColor: 'rgb(16, 185, 129)',",
            "                            borderWidth: 1",
            "                        }]",
            "                    },",
            "                    options: {",
            "                        responsive: true,",
            "                        plugins: {",
            "                            title: {",
            "                                display: true,",
            "                                text: 'MAP Performance'",
            "                            },",
            "                        },",
            "                        scales: {",
            "                            y: {",
            "                                beginAtZero: true,",
            "                                max: 1",
            "                            }",
            "                        }",
            "                    }",
            "                });",
            "                ",
            "                // Create MRR chart",
            "                new Chart(document.getElementById('mrrChart'), {",
            "                    type: 'bar',",
            "                    data: {",
            "                        labels: chartData.mrr.labels,",
            "                        datasets: [{",
            "                            label: 'MRR Score',",
            "                            data: chartData.mrr.values,",
            "                            backgroundColor: 'rgba(245, 158, 11, 0.6)',",
            "                            borderColor: 'rgb(245, 158, 11)',",
            "                            borderWidth: 1",
            "                        }]",
            "                    },",
            "                    options: {",
            "                        responsive: true,",
            "                        plugins: {",
            "                            title: {",
            "                                display: true,",
            "                                text: 'MRR Performance'",
            "                            },",
            "                        },",
            "                        scales: {",
            "                            y: {",
            "                                beginAtZero: true,",
            "                                max: 1",
            "                            }",
            "                        }",
            "                    }",
            "                });",
            "            });",
            "        </script>",
            "    </div>",
            "</body>",
            "</html>",
        ])
        
        html_report = "\n".join(html_parts)
        
        if output_file:
            # If the output file doesn't end with .html, add .html extension
            if not output_file.lower().endswith(".html"):
                output_file = f"{output_file}.html"
                
            with open(output_file, "w") as f:
                f.write(html_report)
        
        return html_report