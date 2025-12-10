# RAG Application Evaluation Guide

This guide explains how to evaluate your RAG application's performance using the included evaluation scripts and metrics.

## Table of Contents

1. [Overview](#overview)
2. [Evaluation Metrics](#evaluation-metrics)
3. [Evaluation Scripts](#evaluation-scripts)
4. [Running Evaluations](#running-evaluations)
5. [Interpreting Results](#interpreting-results)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Overview

The RAG application includes comprehensive evaluation capabilities to assess:
- **Answer Quality**: How well the system answers questions
- **Retrieval Quality**: How well the system retrieves relevant context
- **Faithfulness**: Whether answers are grounded in retrieved context
- **Relevancy**: Whether answers and context are relevant to queries

Evaluations can be run on:
- **Conversation Logs**: Real user interactions stored in `logs/rag_turns.jsonl`
- **Golden Datasets**: Test cases with expected answers and context

## Evaluation Metrics

### Reference-Free Metrics

These metrics don't require ground truth (expected answers) and can be used on any conversation logs.

#### 1. Faithfulness

**What it measures**: Whether the answer is derived from and supported by the retrieved context.

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- **0.8-1.0**: Answer is highly faithful to context (excellent)
- **0.6-0.8**: Answer is mostly faithful (good)
- **0.4-0.6**: Answer has some faithfulness issues (fair)
- **0.0-0.4**: Answer is not faithful to context (poor)

**Use case**: Detects hallucinations and answers that go beyond the provided context.

#### 2. Answer Relevancy

**What it measures**: How relevant the answer is to the user's query.

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- **0.8-1.0**: Answer is highly relevant (excellent)
- **0.6-0.8**: Answer is mostly relevant (good)
- **0.4-0.6**: Answer has some relevancy issues (fair)
- **0.0-0.4**: Answer is not relevant (poor)

**Use case**: Detects cases where the system answers a different question than asked.

#### 3. Contextual Relevancy

**What it measures**: How relevant the retrieved context chunks are to the query.

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- **0.8-1.0**: Context is highly relevant (excellent)
- **0.6-0.8**: Context is mostly relevant (good)
- **0.4-0.6**: Context has some relevancy issues (fair)
- **0.0-0.4**: Context is not relevant (poor)

**Use case**: Identifies retrieval problems - when the system retrieves irrelevant chunks.

### Reference-Based Metrics

These metrics require ground truth (expected answers/context) and are used with golden datasets.

#### 4. Contextual Precision

**What it measures**: Whether relevant chunks are ranked higher in the retrieval results.

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- **0.8-1.0**: Highly precise retrieval (excellent)
- **0.6-0.8**: Mostly precise retrieval (good)
- **0.4-0.6**: Some precision issues (fair)
- **0.0-0.4**: Low precision (poor)

**Use case**: Measures retrieval ranking quality - ensures the most relevant chunks appear first.

#### 5. Contextual Recall

**What it measures**: Whether the retrieved context contains the information needed to answer the question (compared to expected context).

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- **0.8-1.0**: High recall - retrieved most/all needed context (excellent)
- **0.6-0.8**: Good recall - retrieved most needed context (good)
- **0.4-0.6**: Fair recall - retrieved some needed context (fair)
- **0.0-0.4**: Low recall - missed important context (poor)

**Use case**: Measures whether retrieval finds all necessary information to answer the question.

## Evaluation Scripts

The application includes two evaluation scripts:

### 1. `evaluation/evaluate_logs.py`

**Purpose**: Reference-free evaluation on conversation logs (no ground truth needed).

**Metrics**: Faithfulness, Answer Relevancy, Contextual Relevancy (3 metrics)

**Requirements**:
- Conversation logs in `logs/rag_turns.jsonl`
- Ollama running with evaluation model (`qwen3:0.6b`)

**Features**:
- Suitable for continuous monitoring
- No golden dataset required
- Can filter by chunking strategy
- Can limit number of records

### 2. `evaluation/evaluate_goldens.py`

**Purpose**: Reference-based evaluation using a golden dataset with expected answers.

**Metrics**: Contextual Precision, Contextual Recall (2 metrics)

**Requirements**:
- Golden dataset JSON file with expected outputs
- Running RAG API server (`python run_server.py`)
- Ollama running with evaluation model (`deepseek-r1:1.5b`)

**Features**:
- Compares actual RAG responses to expected outputs
- Queries the live RAG API
- Requires ground truth data

## Running Evaluations

### Prerequisites

Before running evaluations:

1. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```

2. **Pull evaluation models** (if not already done):
   ```bash
   ollama pull qwen3:0.6b        # For log evaluations
   ollama pull deepseek-r1:1.5b  # For golden evaluation (if using same as LLM)
   ```

3. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

### Running Reference-Free Log Evaluation

Evaluate conversation logs using reference-free metrics (no ground truth required):

```bash
cd /path/to/RAG_App
source venv/bin/activate
python evaluation/evaluate_logs.py
```

**Expected Output**:
```
Starting offline DeepEval evaluation (Reference-Free Metrics)...
Using Ollama model: qwen3:0.6b
Ollama base URL: http://localhost:11434
Log path: logs/rag_turns.jsonl
Max records: No limit
Filter strategy: All strategies

Loaded 50 records from log file
Evaluating 50 records

Evaluating test cases using Ollama model: qwen3:0.6b...
  Processed 10/50 test cases...
  Processed 20/50 test cases...
  ...
Completed evaluation of 50 test cases

============================================================
Evaluation Summary
============================================================
Total records evaluated: 50

AnswerRelevancyMetric:
  Mean:   0.8234
  StdDev: 0.1234
  Min:    0.5678
  Max:    0.9876

FaithfulnessMetric:
  Mean:   0.7890
  StdDev: 0.1456
  Min:    0.4321
  Max:    0.9876

ContextualRelevancyMetric:
  Mean:   0.7567
  StdDev: 0.1123
  Min:    0.5432
  Max:    0.9123
```

**Filtering by Chunking Strategy**:

Edit the script to filter by strategy:
```python
# In evaluation/evaluate_logs.py
FILTER_STRATEGY = "docling"  # or "recursive_text_splitter"
```

**Limiting Records**:

Edit the script to limit evaluation:
```python
# In evaluation/evaluate_logs.py
MAX_RECORDS = 10  # Only evaluate first 10 records
```

### Running Golden Dataset Evaluation

1. **Prepare Golden Dataset**:

Create a JSON file with test cases:
```json
[
  {
    "input": "What is the main topic of the document?",
    "expected_output": "The document discusses machine learning fundamentals.",
    "context": ["Document chunk 1 about ML...", "Document chunk 2 about ML..."]
  },
  {
    "input": "Who is the author?",
    "expected_output": "The author is John Doe.",
    "context": ["Document chunk mentioning author John Doe..."]
  }
]
```

2. **Start RAG API Server** (in a separate terminal):
   ```bash
   python run_server.py
   ```

3. **Run Evaluation**:

Edit `evaluation/evaluate_goldens.py` to set the golden dataset path:
```python
DEFAULT_GOLDENS_PATH = "path/to/your/golden_dataset.json"
```

Then run:
```bash
python evaluation/evaluate_goldens.py
```

**Expected Output**:
```
Loading golden dataset from TestNotebooks/synthetic_data/my_dataset.json...
Loaded 10 golden test cases

Querying RAG API for each test case...
  Processed 5/10 test cases...
  Processed 10/10 test cases...

Evaluating test cases using Ollama model: deepseek-r1:1.5b...
  Processed 5/10 test cases...
  Processed 10/10 test cases...

============================================================
Evaluation Summary
============================================================
Total records evaluated: 10

ContextualPrecisionMetric:
  Mean:   0.8567
  StdDev: 0.0987
  Min:    0.6543
  Max:    0.9876

ContextualRecallMetric:
  Mean:   0.8123
  StdDev: 0.1123
  Min:    0.5678
  Max:    0.9876
```

## Interpreting Results

### Understanding Score Ranges

**Excellent (0.8-1.0)**:
- System is performing very well
- Answers are faithful, relevant, and retrieval is accurate
- Minor improvements possible but not critical

**Good (0.6-0.8)**:
- System is performing well
- Some room for improvement
- Consider tuning retrieval parameters (TOP_K) or chunking strategy

**Fair (0.4-0.6)**:
- System needs improvement
- Review chunking strategy, retrieval parameters, or model selection
- Check if documents are being indexed correctly

**Poor (0.0-0.4)**:
- System needs significant improvement
- Review entire pipeline:
  - Document processing and chunking
  - Embedding model quality
  - Retrieval configuration
  - LLM prompt engineering

### Comparing Metrics

**High Faithfulness + Low Answer Relevancy**:
- System is faithful to context but may be answering the wrong question
- Check if retrieval is finding relevant chunks
- Review query understanding

**High Answer Relevancy + Low Faithfulness**:
- System understands queries but may be hallucinating
- Check if retrieved context is sufficient
- Review LLM prompt to emphasize using only provided context

**Low Contextual Relevancy**:
- Retrieval is finding irrelevant chunks
- Consider:
  - Adjusting TOP_K (retrieving more chunks)
  - Improving chunking strategy
  - Reviewing embedding model quality

**Low Contextual Recall**:
- Retrieval is missing important information
- Consider:
  - Increasing TOP_K
  - Improving chunking to preserve context
  - Reviewing document indexing

### Grouped Results by Strategy

If your logs contain multiple chunking strategies, the evaluation will group results:

```
Found 2 chunking strategies: ['docling', 'recursive_text_splitter']

============================================================
Strategy: docling
============================================================
Total records evaluated: 30
...

============================================================
Strategy: recursive_text_splitter
============================================================
Total records evaluated: 20
...
```

This allows you to compare different chunking strategies and choose the best one.

## Configuration

### Changing Evaluation Models

Edit the evaluation scripts to use different Ollama models:

```python
# In evaluation/evaluate_logs.py
OLLAMA_MODEL = "qwen3:0.6b"  # Change to your preferred model
OLLAMA_BASE_URL = "http://localhost:11434"
```

```python
# In evaluation/evaluate_goldens.py
OLLAMA_MODEL = "deepseek-r1:1.5b"  # Change to your preferred model
```

### Changing Log Path

Edit the scripts to use a different log file:

```python
LOG_PATH = "logs/rag_turns.jsonl"  # Change to your log file path
```

Or set via environment variable:
```bash
export RAG_LOG_PATH="logs/custom_logs.jsonl"
python evaluation/evaluate_logs.py
```

### Changing API URL (Golden Evaluation)

If your RAG API runs on a different port:

```python
# In evaluation/evaluate_goldens.py
API_URL = "http://localhost:8001/api/chat"  # Change port if needed
```

## Troubleshooting

### Evaluation Script Issues

**Problem**: `ModuleNotFoundError: No module named 'deepeval'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Problem**: `Connection refused` to Ollama
- **Solution**: Ensure Ollama is running: `ollama serve`

**Problem**: Model not found errors
- **Solution**: Pull the required model: `ollama pull qwen3:0.6b`

**Problem**: Log file not found
- **Solution**: 
  - Check `RAG_LOG_PATH` environment variable or script configuration
  - Ensure logs exist: `ls logs/rag_turns.jsonl`
  - Upload some documents and have conversations to generate logs

### Golden Dataset Issues

**Problem**: `Connection refused` to RAG API
- **Solution**: Ensure backend server is running: `python run_server.py`

**Problem**: Golden dataset file not found
- **Solution**: 
  - Check `DEFAULT_GOLDENS_PATH` in the script
  - Ensure the JSON file exists and is valid JSON

**Problem**: Invalid JSON in golden dataset
- **Solution**: Validate JSON format. Each entry needs:
  - `input`: The question
  - `expected_output`: Expected answer
  - `context`: List of expected context chunks

### Performance Issues

**Problem**: Evaluation is very slow
- **Solution**: 
  - Limit records: Set `MAX_RECORDS = 10` for testing
  - Use smaller evaluation models
  - Evaluation is inherently slow (LLM calls for each metric)

**Problem**: Out of memory errors
- **Solution**: 
  - Reduce `MAX_RECORDS`
  - Process evaluations in batches
  - Close other applications using memory

### Result Interpretation Issues

**Problem**: All scores are very low (< 0.3)
- **Solution**: 
  - Check if documents are being indexed correctly
  - Verify Ollama models are working: `ollama run qwen3:0.6b "test"`
  - Review log file format - ensure it has required fields

**Problem**: Scores vary widely (high std dev)
- **Solution**: 
  - This is normal - different queries have different difficulty
  - Review individual test cases to understand patterns
  - Consider filtering out edge cases

## Best Practices

1. **Regular Evaluation**: Run evaluations periodically to monitor system performance
2. **Baseline Establishment**: Run evaluation on initial dataset to establish baseline scores
3. **A/B Testing**: Compare different configurations (chunking strategies, TOP_K values)
4. **Golden Dataset Maintenance**: Keep golden dataset updated as documents change
5. **Log Analysis**: Review low-scoring cases to identify improvement opportunities
6. **Metric Selection**: Use reference-free metrics for continuous monitoring, reference-based for detailed analysis

## Additional Resources

- [DeepEval Documentation](https://docs.confident-ai.com/)
- [RAG Evaluation Best Practices](https://python.langchain.com/docs/use_cases/evaluation/)
- [Understanding RAG Metrics](https://www.pinecone.io/learn/rag-evaluation/)
