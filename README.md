# pinecone-evals
Experimental Python client for Pinecone Evaluation API

## Overview

The Pinecone Evals library allows you to evaluate and compare different search configurations using standardized metrics. It provides a simple, intuitive interface for:

- Creating search profiles with different configurations
- Evaluating those profiles with test queries
- Comparing performance metrics to identify optimal settings

> **⚠️ Beta Warning**  
> This library is currently in beta. APIs may change and stability is not guaranteed. Use in production environments at your own risk.
## Installation

Install directly from the repository:

```bash
git clone https://github.com/pinecone-io/pinecone-evals.git
cd pinecone-evals
pip install -e .
```

Or install from GitHub without cloning:

```bash
pip install git+https://github.com/pinecone-io/pinecone-evals.git
```

## Quick Start

```python
from pinecone_evals import PineconeEval, SearchEvaluator, Query, SearchHit, SearchResult

# Initialize the evaluation client
eval_client = PineconeEval(api_key="your_api_key_here")

# Create an evaluator
evaluator = SearchEvaluator(eval_client)

# Define test queries
test_queries = [
    Query(text="what is the capital of france?"),
    Query(text="best practices for vector search")
]

# Define your search function
def my_search_function(query: Query) -> SearchResult:
    # This would call your actual search API
    # For example, querying your Pinecone index
    hits = [
        SearchHit(id="doc1", text="Paris is the capital of France."),
        SearchHit(id="doc2", text="France is a country in Western Europe.")
    ]
    return SearchResult(query=query, hits=hits)

# Evaluate the search approach
results = evaluator.evaluate_approach(
    name="my_approach", 
    search_fn=my_search_function, 
    queries=test_queries
)

# Generate a report
report = evaluator.generate_report("evaluation_report.md")
```

## Creating Your Own Search Implementation

To evaluate your own Pinecone-based search system:

1. Create a search function that connects to your Pinecone index:

```python
from pinecone_evals import Query, SearchHit, SearchResult
from pinecone import Pinecone

pc = Pinecone(api_key="your_api_key")
index = pc.Index("your-index-name")

    
def pinecone_search(query: Query) -> SearchResult:
    # Initialize Pinecone and connect to your index
    
    # Search the index
    results = index.search_records(query={"inputs": {"text": query.text}})
    
    # Format results as SearchHit objects
    hits = []
    for match in results['result']['hits']:
        hits.append(SearchHit(**match['fields']))
    
    return SearchResult(query=query, hits=hits)
```

2. Define test queries:

```python
from pinecone_evals import Query

test_queries = [
    Query(text="how do neural networks work?"),
    Query(text="what is vector search?")
]
```

3. Evaluate your search implementation:

```python
from pinecone_evals import PineconeEval, SearchEvaluator

evaluator = SearchEvaluator(PineconeEval(api_key="your_api_key"))
evaluator.evaluate_approach("my_pinecone_search", pinecone_search, test_queries)

evaluator.generate_report("run_evals.html", format="html")
```

For a complete working example, see [examples/custom_search_template.py](examples/custom_search_template.py)

## Using the Eval API Directly 

The library uses Pinecone's evaluation API to assess search results:

### Request

```shell
curl -X POST https://api.pinecone.io/evals \
  -H "Content-Type: application/json" \
  -H "Api-Key: <APIKEY-HERE>" \
  -d '{
    "query": {
      "inputs": {
        "text": "What are the benefits of renewable energy?"
      }
    },
    "eval": {
      "debug": true,
      "fields": ["chunk_text"]
    },
    "hits": [
      {
        "chunk_text": "Renewable energy provides sustainable power, reduces greenhouse gas emissions, and helps mitigate climate change by leveraging natural resources."
      },
      {
        "chunk_text": "Renewable energy is seen as an alternative to fossil fuels and can be crucial in reducing carbon footprints, though its implementation might face technical challenges."
      }
    ]
  }'
```

## Available Metrics

The library calculates the following metrics:

- **NDCG (Normalized Discounted Cumulative Gain)**: Measures ranking quality
- **MAP (Mean Average Precision)**: Evaluates precision at different recall levels
- **MRR (Mean Reciprocal Rank)**: Measures position of first relevant result

## Command Line Interface

Evaluate search results directly from the command line:

```bash
python -m pinecone_evals.cli --api-key YOUR_API_KEY --queries queries.json --hits hits.json --output results.json
```

## License

See the LICENSE file for details.