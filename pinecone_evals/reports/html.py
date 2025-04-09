import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader


def generate_html_report(
    results: Dict[str, Any],
    comparison: Dict[str, Any],
    output_file: Optional[str] = None,
) -> str:
    """Generate an interactive HTML report of the evaluation results.

    Args:
        results: Dictionary with evaluation results by approach name
        comparison: Dictionary with comparison data
        output_file: Optional file path to write the report to

    Returns:
        The generated report as a string
    """
    approaches = list(results.keys())

    # Setup Jinja2 environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))

    # Add custom filter to convert Python objects to JSON strings
    env.filters["tojson"] = lambda obj: json.dumps(obj)

    # Prepare data for charts
    chart_data = _prepare_chart_data(results)
    color_map = _prepare_color_map(approaches)

    # Prepare data for best approaches per query
    best_approaches = _prepare_best_approaches(results)

    # Render template with data
    template = env.get_template("report.html")
    html_report = template.render(
        results=results,
        comparison=comparison,
        approaches=approaches,
        chart_data=chart_data,
        color_map=color_map,
        best_approaches=best_approaches,
    )

    # Write to file if output_file is specified
    if output_file:
        # If the output file doesn't end with .html, add .html extension
        if not output_file.lower().endswith(".html"):
            output_file = f"{output_file}.html"

        with open(output_file, "w") as f:
            f.write(html_report)

    return html_report


def _prepare_chart_data(results: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data for charts."""
    approaches = list(results.keys())
    metrics = list(next(iter(results.values()))["metrics"].keys())

    chart_data = {}
    for metric in metrics:
        metric_values = [
            results[approach]["metrics"][metric]["mean"] for approach in approaches
        ]
        chart_data[metric] = {
            "labels": approaches,
            "values": metric_values,
            "best_approach": approaches[metric_values.index(max(metric_values))],
            "best_value": max(metric_values),
        }

    return chart_data


def _prepare_color_map(approaches: List[str]) -> Dict[str, Dict[str, str]]:
    """Prepare color mapping for approaches."""
    colors = [
        "rgb(79, 70, 229)",  # Indigo
        "rgb(16, 185, 129)",  # Green
        "rgb(245, 158, 11)",  # Amber
        "rgb(239, 68, 68)",  # Red
        "rgb(59, 130, 246)",  # Blue
        "rgb(217, 70, 239)",  # Purple
        "rgb(20, 184, 166)",  # Teal
        "rgb(232, 121, 249)",  # Fuchsia
    ]

    color_map = {}
    for i, approach in enumerate(approaches):
        color_index = i % len(colors)
        color_map[approach] = {
            "fill": colors[color_index].replace("rgb", "rgba").replace(")", ", 0.6)"),
            "border": colors[color_index],
        }

    return color_map


def _prepare_best_approaches(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Prepare data for best approach per query section."""
    approaches = list(results.keys())

    # Find a result with detailed_results to get queries
    detailed_approach = next(
        (app for app in approaches if "detailed_results" in results[app]), None
    )

    if not detailed_approach:
        return []

    queries = [r.query.text for r in results[detailed_approach]["detailed_results"]]

    best_approaches = []
    for i, query in enumerate(queries):
        query_data = {"query": query}

        for metric in ["ndcg", "map", "mrr"]:
            best_score = -1
            best_approach = ""

            for approach in approaches:
                if "detailed_results" not in results[approach]:
                    continue

                metrics_dict = results[approach]["detailed_results"][i].metrics
                approach_score = metrics_dict.get(metric, 0)
                if approach_score > best_score:
                    best_score = approach_score
                    best_approach = approach

            query_data[metric] = {"approach": best_approach, "score": best_score}

        best_approaches.append(query_data)

    return best_approaches
