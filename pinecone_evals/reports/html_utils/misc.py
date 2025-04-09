"""Report generation utilities for search evaluation."""

from html import escape
from typing import Any, Dict, List

from pinecone_evals.reports.html_utils.generate_query_result import _generate_query_result


def _generate_charts_section() -> List[str]:
    """Generate the charts section HTML."""
    return [
        '        <div class="bg-white rounded-lg shadow p-6 mb-8">',
        '            <h2 class="text-xl font-semibold mb-4">Comparison Charts</h2>',
        '            <div id="chart-legend" class="flex justify-center mb-4"></div>',
        '            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">',
        '                <div class="h-80">',
        '                    <canvas id="ndcgChart"></canvas>',
        "                </div>",
        '                <div class="h-80">',
        '                    <canvas id="mapChart"></canvas>',
        "                </div>",
        '                <div class="h-80">',
        '                    <canvas id="mrrChart"></canvas>',
        "                </div>",
        "            </div>",
        "        </div>",
    ]


def _generate_approach_tabs(approaches: List[str]) -> List[str]:
    """Generate the approach tabs navigation."""
    html_parts = [
        '        <div class="bg-white rounded-lg shadow mb-8">',
        '            <div class="flex overflow-x-auto border-b">',
    ]

    # Add approach tabs
    for i, approach in enumerate(approaches):
        active_class = " active" if i == 0 else ""
        html_parts.append(
            f'                <button class="approach-tab px-6 py-3 font-medium{active_class}" onclick="showTab(\'{approach}\')">{escape(str(approach))}</button>'
        )

    html_parts.append("            </div>")

    return html_parts


def _generate_approach_content(
        approach_name: str, approach_data: Dict[str, Any], is_active: bool
) -> List[str]:
    """Generate the content for a specific approach."""
    active_class = " active" if is_active else ""

    html_parts = [
        f'                <div id="{approach_name}-tab" class="tab-content{active_class}">',
        f'                    <h3 class="text-lg font-semibold mb-4">{escape(str(approach_name))}</h3>',
        # Metrics table
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
    ]

    for metric, stats in approach_data["metrics"].items():
        html_parts.extend(
            [
                "                                <tr>",
                f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{escape(str(metric))}</td>',
                f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["mean"]:.4f}</td>',
                f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["median"]:.4f}</td>',
                f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["min"]:.4f}</td>',
                f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["max"]:.4f}</td>',
                f'                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{stats["stddev"]:.4f}</td>',
                "                                </tr>",
            ]
        )

    html_parts.extend(
        [
            "                            </tbody>",
            "                        </table>",
            "                    </div>",
        ]
    )

    # Per-query results with expandable details
    if "detailed_results" in approach_data:
        html_parts.extend(
            [
                '                    <h4 class="text-md font-semibold mb-2">Query Results</h4>',
                '                    <div class="space-y-4">',
            ]
        )

        for j, result in enumerate(approach_data["detailed_results"]):
            html_parts.extend(_generate_query_result(approach_name, j, result))

        html_parts.append("                    </div>")

    html_parts.append("                </div>")

    return html_parts


def _generate_hit_score(index: int, hit_score: Any) -> List[str]:
    """Generate HTML for a hit score."""
    justification = hit_score.justification
    relevant_class = "relevant" if hit_score.relevant else "not-relevant"

    return [
        f'                                    <div class="hit {relevant_class} p-3">',
        '                                        <div class="flex justify-between items-center mb-2">',
        f'                                            <span class="font-medium text-gray-800">Result #{index + 1} · ID: {escape(str(hit_score.hit_id))}</span>',
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
        "                                        </div>",
        "                                    </div>",
    ]


