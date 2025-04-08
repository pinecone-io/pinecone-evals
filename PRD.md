# Problem

---

Evaluating search quality is difficult due to the dynamic nature of both user queries and the underlying data. To evaluate the quality of a system typically requires human annotators or clickstream data. However both these approaches are difficult to cold-start or are labor intensive, limiting their use to new products or features. Without the ability to evaluate the quality of their system, it is difficult for a user to understand limitations of their system and for them to take deliberate steps to improve it. While there are many tools that have support LLM evaluations, few are focused on the particular challenges of retrieval and they require users to adopt a new suite of tools. 

### High Level Solution

We will develop a retrieval evaluation system powered by LLMs to assess search quality. The initial version will provide an evaluation API that takes a user query and ranked list of records as input, then returns both individual relevance scores for each record and an overall request score. Future versions will support continuous evaluation of search results through integrated inference.

### Goals

- Simplify the process for customers to evaluate their retrieval quality
- Enable the field team in running evaluations of new capabilities for customers like sparse or rerank
- Educate users about how to measure end-to-end retrieval quality
- Drive adoption of integrated inference by offering simplified access to evaluation capabilities

### Non Goals

- Solve a wider range of LLM evaluations problems

# Solution

---

Traditionally, human annotators or clickstream data are used to generate datasets for retrieval evaluation. However  challenging for new teams to cold-start or initiate. Recent research indicates that LLMs can rival human annotators' performance, opening up a new, highly scalable approach to creating retrieval evaluations. These methods are not perfect and the performance across a wider variety of use cases remains an open question.

## Key Features

---

### Eval Score

The LLM will generate a relevance score for each document on the search results on a score from 1-4. Anything less than ≥ 3 will be considered relevant for binary judgements. The quality of evaluation is critical, necessitating the use of more powerful models like o3. 

- `Highly Relevant (4)` - Document precisely addresses the core query, provides comprehensive and directly applicable content, contains no irrelevant information, and is factually accurate with significant insight
- `Moderately Relevant (3)` - Document addresses a substantial portion of the query but may miss some key elements, provides useful information but lacks full comprehensiveness, and contains only minor irrelevant details
- `Partially Relevant (2)` - Document touches on query-related aspects but lacks depth, contains notable irrelevant content, and has weak connections requiring additional context
- `Not Relevant (1)` - Document fails to address the query, contains primarily irrelevant content, and provides no meaningful insight or utility

### Relevance Metrics

The eval API will return retrieval metrics that help the user understand the quality of the query based on the presence and order of 

`NDCG` **(Normalized Discounted Cumulative Gain)**

Measures the quality of ranking by considering both relevance and position. It penalizes highly relevant documents appearing lower in the results. `rel_i` is the eval score of the document.

$$
NDCG@k = \frac{DCG@k}{IDCG@k}

DCG@k = \sum_{i=1}^k \frac{2^{rel_i} - 1}{\log_2(i + 1)}
$$

**`MAP` (Mean Average Precision)**

Calculates the mean of average precision scores for each query, where documents with scores ≥3 are considered relevant. 

$$
MAP = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{\sum_{k=1}^n P(k) \times rel(k)}{number\:of\:relevant\:documents}

$$

`MRR` **(Mean Reciprocal Rank)**

Measures the position of the first relevant result (score ≥3). It focuses on finding the first good answer.

$$
MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}

$$

## LLM

We will use Azure OpenAI, but we can consider other solutions in the future. `o3-mini` will likely perform the best for this task. A LLM prompt that evaluates whether a `passage` is relevant to the specified `query`. The following approach users the [TICK prompting technique](https://arxiv.org/pdf/2410.03608).

- https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-2

### Proposed

```
Evaluate the relevance of the retrieved passage to the given query.

**Scoring Guidelines:**

For each snippet, evaluate using the following YES/NO questions based on the given criteria. Answering YES indicates the snippet satisfies the specific requirement, while answering NO indicates it does not.

### **Highly Relevant (Score: 3)**
- [ ] Does the snippet precisely address the core informational need expressed in the query?
- [ ] Is the content comprehensive and directly applicable, covering all key points of the query?
- [ ] Does the snippet contain no irrelevant or extraneous information?
- [ ] Is the response factually accurate and providing significant insight related to the query?

### **Moderately Relevant (Score: 2)**
- [ ] Does the snippet address a substantial portion of the query, even if some key elements are missing?
- [ ] Is the information useful and directly applicable, though potentially lacking comprehensiveness or depth?
- [ ] Does the snippet include only minor irrelevant details that do not significantly detract from its overall usefulness?

### **Partially Relevant (Score: 1)**
- [ ] Does the snippet touch on aspects related to the query, but lacks depth or covers only a small part?
- [ ] Is there a notable amount of irrelevant content that makes it harder to extract useful information?
- [ ] Is the connection to the query weak, requiring additional context to be useful?

### **Not Relevant (Score: 0)**
- [ ] Does the snippet fail to address the query or provide meaningful information?
- [ ] Is the content primarily irrelevant or off-topic?
- [ ] Does the snippet fail to provide any insight or utility for the query?

[BEGIN DATA]
************
[Query]

{query}
************
[Passage]

{passage}

************
[END DATA]

**Final Step: Provide a Score and Confidence Rating**
- Based on the checklist, provide an overall relevance score (0-3) for each snippet.
- Additionally, provide a confidence score (between 1 and 5) indicating your certainty about the relevance judgment.
```

**Papers**

- https://arxiv.org/pdf/2404.12272
- https://arxiv.org/pdf/2410.21549

## REST API

The user can send the response from an integrated inference call or construct the object themselves.

### Request

```json
{
  "query": {
    "inputs": {
      "text": "what is the capital of france?"
    }
  },
  "eval": {
    // 1 field to start
    "fields": [
      "text"
    ],
    // True | False
    "debug": False
  },
  "hits": [
    {
      "id": "a",
      "text": "Paris is the capital and largest city of France."
    },...
  ]
}
```

### Response

Respond with the LLM judgments. Per Hit return the LLM eval_score and the metrics for the search result.

```json
{
  "metrics": {
      "ndcg": 0.95,
	    "map": 0.90,
	    "mrr": 1.0
  },
  "hits": [
	    {
	      "index": 0, // system
	      "fields": {
			      "id": "a",
			      "text": "foo bar baz"
	      },
	      "relevant": true,
	      "justification": ""
	      },
	    },
	  ]
  },
  "usage": {
		  "evaluation_input_tokens": 30000
  }
}
```

## Key Workflows

---

We expect the primary use case to be running evaluation jobs at infrequent intervals.

### Bulk Evaluation

**User Goal:** Understand the quality of a search system

```python
queries = ["what is the capital of paris", ...]
index = pc.Index("wikipedia")
evals = []
for query in queries:
		query_req = {"inputs": "text": query}
		search_resp = index.search(
				query={"inputs": "text": query}
				fields=["chunk_text"]
		)
		eval_resp = pc.inference.eval_search(
				query=query_req,
				result=search_resp.hits
		)
		evals.append(eval_resp)

ncdg = []
mrr = []
for eval in evals:
		ncdg.append(eval['metrics']['ndcg'])
		...

print("Results")
print("NDCG", sum(ndcg) / len(ndcg))
```

### Compare Retrieval Approaches

**User Goal:** A user wants to understand the benefit of using reranking on their retrieval quality.

```python
queries = ["what is the capital of paris", ...]
index = pc.Index("wikipedia")

## Run eval loops

### Run with Cohere 
index.search(
			...
			rerank={
			   model="cohere-rerank-3.5"
			}
)

###  Run with BGE
index.search(
			...
			rerank={
			   model="bge-rerank-m3-v2"
			}
)

# Comparse results

```