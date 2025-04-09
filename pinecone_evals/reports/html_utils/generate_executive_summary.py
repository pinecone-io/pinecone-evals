from typing import Dict, Any, List


def _generate_executive_summary(
    results: Dict[str, Any], comparison: Dict[str, Any]
) -> List[str]:
    """Generate the executive summary section."""
    approaches = list(results.keys())
    metrics = list(next(iter(results.values()))["metrics"].keys())

    html_parts = [
        '        <div class="bg-white rounded-lg shadow p-6 mb-8">',
        '            <h2 class="text-xl font-semibold mb-4">Summary</h2>',
        '            <div class="prose max-w-none">',
        f'                <p class="mb-2">Comparing {len(approaches)} search approaches: <strong>{", ".join(approaches)}</strong></p>',
        '                <div class="mt-4">',
    ]

    # Add performance comparison table
    html_parts.extend(
        [
            '                    <div class="overflow-x-auto">',
            '                        <table class="min-w-full divide-y divide-gray-200 text-sm mb-4">',
            '                            <thead class="bg-gray-50">',
            "                                <tr>",
            '                                    <th scope="col" class="px-4 py-2 text-left font-medium text-gray-500">Approach</th>',
        ]
    )

    # Table headers for each metric
    for metric in metrics:
        html_parts.append(
            f'                                    <th scope="col" class="px-4 py-2 text-left font-medium text-gray-500">{metric.upper()}</th>'
        )

    html_parts.append("                                </tr>")
    html_parts.append("                            </thead>")
    html_parts.append(
        '                            <tbody class="bg-white divide-y divide-gray-200">'
    )

    # Generate rows for each approach
    for approach in approaches:
        approach_scores = [
            results[approach]["metrics"][metric]["mean"] for metric in metrics
        ]

        # Start the row
        html_parts.append("                                <tr>")
        html_parts.append(
            f'                                    <td class="px-4 py-2 font-medium text-gray-900">{approach}</td>'
        )

        # Add score cells for each metric
        for i, metric in enumerate(metrics):
            score = approach_scores[i]
            best_approach = comparison[metric]["best_approach"]
            is_best = approach == best_approach

            cell_class = "px-4 py-2"
            if is_best:
                cell_class += " font-bold bg-green-50 text-green-800"

            html_parts.append(
                f'                                    <td class="{cell_class}">{score:.4f}</td>'
            )

        html_parts.append("                                </tr>")

    html_parts.extend(
        [
            "                            </tbody>",
            "                        </table>",
            "                    </div>",
        ]
    )

    # Only show performance gaps if there are multiple approaches
    if len(approaches) > 1:
        html_parts.append('                    <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">')
        html_parts.append('                        <h3 class="text-md font-medium mb-2">Performance Gaps</h3>')

        for metric in metrics:
            # Organize all approaches by performance for this metric
            approach_values = [
                (approach, results[approach]["metrics"][metric]["mean"])
                for approach in approaches
            ]
            approach_values.sort(key=lambda x: x[1], reverse=True)

            # Calculate gap percentage between best and worst
            best_value = approach_values[0][1]
            worst_value = approach_values[-1][1]
            diff_percentage = ((best_value - worst_value) / best_value * 100) if best_value > 0 else 0

            best_approach = approach_values[0][0]
            worst_approach = approach_values[-1][0]

            # Only show if the gap is meaningful
            if diff_percentage > 3:
                html_parts.append(
                    f'                        <p class="text-sm mb-1"><span class="font-medium">{metric.upper()}</span>: '
                    f'<span class="text-blue-800">{diff_percentage:.1f}%</span> gap between best and worst</p>'
                )

        html_parts.append('                    </div>')

    html_parts.extend(
        [
            "                </div>",
            "            </div>",
            "        </div>",
        ]
    )

    return html_parts
