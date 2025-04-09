import json
from typing import Dict, Any, List


def _generate_javascript(results: Dict[str, Any]) -> List[str]:
    """Generate the JavaScript section of the HTML report."""
    approaches = list(results.keys())
    metrics = list(next(iter(results.values()))["metrics"].keys())

    # Create chart data
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

    # Generate color palette for approaches
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

    # Create color map for approaches
    color_map = {}
    for i, approach in enumerate(approaches):
        color_index = i % len(colors)
        color_map[approach] = {
            "fill": colors[color_index].replace("rgb", "rgba").replace(")", ", 0.6)"),
            "border": colors[color_index],
        }

    return [
        "        <script>",
        f"            const chartData = {json.dumps(chart_data)};",
        f"            const colorMap = {json.dumps(color_map)};",
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
        "            // Create shared legend",
        "            function createSharedLegend(approaches) {",
        "                const legendContainer = document.getElementById('chart-legend');",
        "                const legendHtml = approaches.map(approach => {",
        "                    const color = colorMap[approach].border;",
        "                    return `<div class='flex items-center mx-2'>",
        "                              <span class='inline-block w-4 h-4 mr-2' style='background-color: ${color}'></span>",
        "                              <span class='text-sm'>${approach}</span>",
        "                           </div>`;",
        "                }).join('');",
        "                legendContainer.innerHTML = legendHtml;",
        "            }",
        "            ",
        "            // Common chart options",
        "            function getChartOptions(metric, title) {",
        "                const bestApproach = chartData[metric].best_approach;",
        "                const bestValue = chartData[metric].best_value;",
        "                ",
        "                return {",
        "                    responsive: true,",
        "                    maintainAspectRatio: false,",
        "                    indexAxis: 'y',",
        "                    plugins: {",
        "                        title: {",
        "                            display: true,",
        "                            text: title + ` (Best: ${bestApproach} - ${bestValue.toFixed(4)})`,",
        "                            font: { size: 14 }",
        "                        },",
        "                        legend: {",
        "                            display: false,",
        "                        },",
        "                        tooltip: {",
        "                            callbacks: {",
        "                                label: function(context) {",
        "                                    return `${context.dataset.label}: ${context.parsed.x.toFixed(4)}`;",
        "                                }",
        "                            }",
        "                        }",
        "                    },",
        "                    scales: {",
        "                        x: {",
        "                            beginAtZero: true,",
        "                            max: 1,",
        "                            title: {",
        "                                display: true,",
        "                                text: 'Score (higher is better)'",
        "                            }",
        "                        },",
        "                        y: {",
        "                            ticks: {",
        "                                crossAlign: 'far'",
        "                            }",
        "                        }",
        "                    }",
        "                };",
        "            }",
        "            ",
        "            // Init charts",
        "            document.addEventListener('DOMContentLoaded', function() {",
        "                // Create shared legend",
        "                createSharedLegend(chartData.ndcg.labels);",
        "                ",
        "                // Create datasets with appropriate color mapping",
        "                function createDatasets(metric, label) {",
        "                    return [{",
        "                        label: label,",
        "                        data: chartData[metric].values,",
        "                        backgroundColor: chartData[metric].labels.map(approach => colorMap[approach].fill),",
        "                        borderColor: chartData[metric].labels.map(approach => colorMap[approach].border),",
        "                        borderWidth: 1",
        "                    }];",
        "                }",
        "                ",
        "                // Create NDCG chart",
        "                new Chart(document.getElementById('ndcgChart'), {",
        "                    type: 'bar',",
        "                    data: {",
        "                        labels: chartData.ndcg.labels,",
        "                        datasets: createDatasets('ndcg', 'NDCG Score')",
        "                    },",
        "                    options: getChartOptions('ndcg', 'NDCG Performance')",
        "                });",
        "                ",
        "                // Create MAP chart",
        "                new Chart(document.getElementById('mapChart'), {",
        "                    type: 'bar',",
        "                    data: {",
        "                        labels: chartData.map.labels,",
        "                        datasets: createDatasets('map', 'MAP Score')",
        "                    },",
        "                    options: getChartOptions('map', 'MAP Performance')",
        "                });",
        "                ",
        "                // Create MRR chart",
        "                new Chart(document.getElementById('mrrChart'), {",
        "                    type: 'bar',",
        "                    data: {",
        "                        labels: chartData.mrr.labels,",
        "                        datasets: createDatasets('mrr', 'MRR Score')",
        "                    },",
        "                    options: getChartOptions('mrr', 'MRR Performance')",
        "                });",
        "            });",
        "        </script>",
        "    </div>",
        "</body>",
        "</html>",
    ]
