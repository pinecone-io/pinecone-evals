from html import escape
from typing import Any, List, Dict

from pinecone_evals.reports.html_utils.misc import  _generate_hit_score


def _generate_query_result(
    approach_name: str, query_index: int, result: Any
) -> List[str]:
    """Generate HTML for a query result with expandable details."""
    query_id = f"{approach_name}-query-{query_index}"

    html_parts = [
        '                        <div class="border border-gray-200 rounded-md">',
        f'                            <div class="flex justify-between items-center p-4 cursor-pointer" onclick="toggleQueryDetails(\'{query_id}\')">',
        f'                                <div class="font-medium">"{escape(str(result.query.text))}"</div>',
        '                                <div class="text-sm bg-blue-100 rounded px-2 py-1">',
    ]

    relevant_hits = sum(1 for score in result.hit_scores if score.relevant)
    total_hits = len(result.hit_scores)
    html_parts.append(
        f"                                    NDCG: {result.metrics.get('ndcg', 0):.4f} | MAP: {result.metrics.get('map', 0):.4f} | MRR: {result.metrics.get('mrr', 0):.4f} | Relevant: {relevant_hits}/{total_hits}"
    )

    html_parts.extend(
        [
            "                                </div>",
            "                            </div>",
            f'                            <div id="{query_id}" class="hidden p-4 bg-gray-50 border-t">',
            '                                <h5 class="font-medium mb-2">Search Results</h5>',
            '                                <div class="space-y-2">',
        ]
    )

    # Show all hits with metadata and highlighting relevance
    for k, hit_score in enumerate(result.hit_scores):
        html_parts.extend(_generate_hit_score(k, hit_score))

    html_parts.extend(
        [
            "                                </div>",
            "                            </div>",
            "                        </div>",
        ]
    )

    return html_parts


def _generate_best_approach_per_query(results: Dict[str, Any]) -> List[str]:
    """Generate the best approach per query section."""
    if len(results) <= 1:
        return []

    html_parts = [
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
    ]

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

    for query_text, approaches_metrics in all_queries.items():
        # Find best approach for each metric
        best_ndcg = max(approaches_metrics.items(), key=lambda x: x[1]["ndcg"])
        best_map = max(approaches_metrics.items(), key=lambda x: x[1]["map"])
        best_mrr = max(approaches_metrics.items(), key=lambda x: x[1]["mrr"])

        html_parts.extend(
            [
                "                        <tr>",
                f'                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">"{escape(str(query_text))}"</td>',
                f'                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="font-medium">{escape(str(best_ndcg[0]))}</span> ({best_ndcg[1]["ndcg"]:.4f})</td>',
                f'                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="font-medium">{escape(str(best_map[0]))}</span> ({best_map[1]["map"]:.4f})</td>',
                f'                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="font-medium">{escape(str(best_mrr[0]))}</span> ({best_mrr[1]["mrr"]:.4f})</td>',
                "                        </tr>",
            ]
        )

    html_parts.extend(
        [
            "                    </tbody>",
            "                </table>",
            "            </div>",
            "        </div>",
        ]
    )

    return html_parts
