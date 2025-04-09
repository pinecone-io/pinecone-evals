from typing import List


def _generate_html_header() -> List[str]:
    """Generate the HTML header section."""
    return [
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
        '        <h1 class="text-3xl font-bold mb-2">Search Evaluation Report</h1>',
        '        <div class="mb-6 bg-white rounded-lg p-4 border border-gray-200 shadow-sm">',
        '            <h3 class="text-md font-medium mb-2">Understanding the Metrics</h3>',
        '            <ul class="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-700">',
        '                <li><strong>NDCG:</strong> Measures ranking quality, considering relevance & position (higher is better)</li>',
        '                <li><strong>MAP:</strong> Evaluates precision at different recall levels (higher is better)</li>',
        '                <li><strong>MRR:</strong> Measures position of first relevant result (higher = earlier)</li>',
        '            </ul>',
        '        </div>',
    ]
