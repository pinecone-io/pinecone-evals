from typing import Dict, Any, Optional

from pinecone_evals.reports import _generate_html_header, _generate_executive_summary, _generate_charts_section, _generate_approach_tabs, _generate_approach_content, _generate_best_approach_per_query, _generate_javascript


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

    # Build the HTML report by combining sections
    html_parts = []

    # Add header section
    html_parts.extend(_generate_html_header())

    # Add executive summary section
    html_parts.extend(_generate_executive_summary(results, comparison))

    # Add charts section
    html_parts.extend(_generate_charts_section())

    # Add approach tabs navigation
    html_parts.extend(_generate_approach_tabs(approaches))

    # Add approach content sections
    html_parts.append('            <div class="p-6">')

    for i, approach_name in enumerate(approaches):
        approach_data = results[approach_name]
        html_parts.extend(
            _generate_approach_content(approach_name, approach_data, i == 0)
        )

    html_parts.append("            </div>")
    html_parts.append("        </div>")

    # Add best approach per query comparison
    html_parts.extend(_generate_best_approach_per_query(results))

    # Add JavaScript for interactivity
    html_parts.extend(_generate_javascript(results))

    # Combine parts into complete HTML document
    html_report = "\n".join(html_parts)

    # Write to file if output_file is specified
    if output_file:
        # If the output file doesn't end with .html, add .html extension
        if not output_file.lower().endswith(".html"):
            output_file = f"{output_file}.html"

        with open(output_file, "w") as f:
            f.write(html_report)

    return html_report
