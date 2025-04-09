from typing import Dict, Any, Optional


def generate_markdown_report(
    results: Dict[str, Any],
    comparison: Dict[str, Any],
    output_file: Optional[str] = None,
) -> str:
    """Generate a Markdown report of the evaluation results.

    Args:
        results: Dictionary with evaluation results by approach name
        comparison: Dictionary with comparison data
        output_file: Optional file path to write the report to

    Returns:
        The generated report as a string
    """
    report = []
    report.append("# Search Evaluation Report")
    report.append("\n## Comparison Summary\n")

    # Create a table of results
    approaches = list(results.keys())
    metrics = list(next(iter(results.values()))["metrics"].keys())

    # Table header
    report.append("| Metric | " + " | ".join(approaches) + " | Best Approach |")
    report.append(
        "|--------|" + "|".join(["---------" for _ in approaches]) + "|-------------|"
    )

    # Table rows
    for metric in metrics:
        values = [
            f"{results[approach]['metrics'][metric]['mean']:.4f}"
            for approach in approaches
        ]
        best = comparison[metric]["best_approach"]
        report.append(f"| {metric} | " + " | ".join(values) + f" | **{best}** |")

    # Add detailed per-approach results
    report.append("\n## Detailed Results\n")

    for approach_name, approach_data in results.items():
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
                relevant_hits = sum(1 for score in result.hit_scores if score.relevant)
                total_hits = len(result.hit_scores)

                report.append(
                    f'| "{query_text}" | {result.metrics.get("ndcg", 0):.4f} | {result.metrics.get("map", 0):.4f} | {result.metrics.get("mrr", 0):.4f} | {relevant_hits}/{total_hits} |'
                )

        report.append("\n")

    # Add a per-query comparison to show best approach for each query
    if len(results) > 1:
        report.append("## Best Approach Per Query\n")

        # Collect all unique queries from all approaches
        all_queries = {}

        for approach_name, approach_data in results.items():
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
        report.append("|-------|--------------|-------------|----------------|")

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
