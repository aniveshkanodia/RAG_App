"""
Offline DeepEval evaluation script for RAG chatbot logs.

Reads RAG turn logs from JSONL file and evaluates them using DeepEval's RAG metrics.
"""

import json
import os
from collections import defaultdict
from statistics import mean, stdev
from typing import List, Dict, Any

from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)

# Configuration constants
LOG_PATH = "logs/rag_turns.jsonl"
MAX_RECORDS = None  # Set to an integer to limit records, or None for no limit
FILTER_STRATEGY = None  # Set to a specific chunking_strategy string to filter, or None to include all

# Ollama configuration
OLLAMA_MODEL = "qwen3:0.6b"
OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama URL

# Metric classes to use for evaluation
METRIC_CLASSES = [
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
]


def read_log_file(log_path: str) -> List[Dict[str, Any]]:
    """Read and parse JSONL log file.
    
    Args:
        log_path: Path to the JSONL log file
        
    Returns:
        List of parsed log records
    """
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at {log_path}")
        return []
    
    records = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed line {line_num}: {e}")
                continue
    
    return records


def filter_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter records based on configuration.
    
    Args:
        records: List of log records
        
    Returns:
        Filtered list of records
    """
    filtered = records
    
    # Filter by chunking strategy if specified
    if FILTER_STRATEGY is not None:
        filtered = [r for r in filtered if r.get('chunking_strategy') == FILTER_STRATEGY]
        print(f"Filtered to {len(filtered)} records with strategy '{FILTER_STRATEGY}'")
    
    # Limit to MAX_RECORDS if specified
    if MAX_RECORDS is not None and MAX_RECORDS > 0:
        filtered = filtered[:MAX_RECORDS]
        print(f"Limited to first {MAX_RECORDS} records")
    
    return filtered


def create_test_cases(records: List[Dict[str, Any]]) -> List[LLMTestCase]:
    """Create DeepEval test cases from log records.
    
    Args:
        records: List of log records
        
    Returns:
        List of LLMTestCase objects
    """
    test_cases = []
    for record in records:
        test_case = LLMTestCase(
            input=record.get('user_query', ''),
            actual_output=record.get('answer', ''),
            retrieval_context=record.get('contexts', [])
        )
        test_cases.append(test_case)
    return test_cases


def get_ollama_model():
    """Get configured Ollama model instance.
    
    Returns:
        OllamaModel instance configured with qwen3:0.6b
    """
    return OllamaModel(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0
    )


def evaluate_test_cases(test_cases: List[LLMTestCase]) -> Dict[str, List[float]]:
    """Evaluate test cases using DeepEval metrics with Ollama.
    
    Args:
        test_cases: List of LLMTestCase objects
        
    Returns:
        Dictionary mapping metric names to lists of scores
    """
    # Initialize Ollama model
    ollama_model = get_ollama_model()
    
    # Store scores for each metric
    metric_scores = defaultdict(list)
    
    # Evaluate each test case with each metric
    print(f"Evaluating test cases using Ollama model: {OLLAMA_MODEL}...")
    for i, test_case in enumerate(test_cases):
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(test_cases)} test cases...")
        
        for metric_class in METRIC_CLASSES:
            try:
                # Create a new metric instance for each test case with Ollama model
                metric = metric_class(model=ollama_model)
                metric.measure(test_case)
                score = metric.score
                if score is not None:
                    metric_scores[metric.__class__.__name__].append(score)
            except Exception as e:
                print(f"  Warning: Failed to evaluate {metric_class.__name__} for test case {i+1}: {e}")
                continue
    
    print(f"Completed evaluation of {len(test_cases)} test cases\n")
    return dict(metric_scores)


def calculate_statistics(scores: List[float]) -> Dict[str, float]:
    """Calculate statistics for a list of scores.
    
    Args:
        scores: List of score values
        
    Returns:
        Dictionary with mean, std, min, max statistics
    """
    if not scores:
        return {}
    
    return {
        'mean': mean(scores),
        'std': stdev(scores) if len(scores) > 1 else 0.0,
        'min': min(scores),
        'max': max(scores),
    }


def print_summary(metric_scores: Dict[str, List[float]], num_records: int, strategy_name: str = None):
    """Print evaluation summary statistics.
    
    Args:
        metric_scores: Dictionary mapping metric names to lists of scores
        num_records: Number of records evaluated
        strategy_name: Optional strategy name to include in header
    """
    print(f"\n{'='*60}")
    if strategy_name:
        print(f"Strategy: {strategy_name}")
    else:
        print(f"Evaluation Summary")
    print(f"{'='*60}")
    print(f"Total records evaluated: {num_records}\n")
    
    if not metric_scores:
        print("No scores available.")
        return
    
    for metric_name, scores in metric_scores.items():
        if not scores:
            print(f"{metric_name}: No scores available")
            continue
        
        stats = calculate_statistics(scores)
        print(f"{metric_name}:")
        print(f"  Mean:   {stats['mean']:.4f}")
        print(f"  StdDev: {stats['std']:.4f}")
        print(f"  Min:    {stats['min']:.4f}")
        print(f"  Max:    {stats['max']:.4f}")
        print()


def evaluate_by_strategy(records: List[Dict[str, Any]]):
    """Evaluate records grouped by chunking strategy.
    
    Args:
        records: List of log records
    """
    # Group records by chunking strategy
    strategy_groups = defaultdict(list)
    for record in records:
        strategy = record.get('chunking_strategy', 'unknown')
        strategy_groups[strategy].append(record)
    
    print(f"\nFound {len(strategy_groups)} chunking strategies: {list(strategy_groups.keys())}\n")
    
    # Evaluate each strategy separately
    for strategy, strategy_records in strategy_groups.items():
        # Create test cases for this strategy
        test_cases = create_test_cases(strategy_records)
        
        # Evaluate
        metric_scores = evaluate_test_cases(test_cases)
        
        # Print summary for this strategy (reusing print_summary function)
        print_summary(metric_scores, len(strategy_records), strategy_name=strategy)


def main():
    """Main evaluation function."""
    print("Starting offline DeepEval evaluation...")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print(f"Ollama base URL: {OLLAMA_BASE_URL}")
    print(f"Log path: {LOG_PATH}")
    print(f"Max records: {MAX_RECORDS if MAX_RECORDS else 'No limit'}")
    print(f"Filter strategy: {FILTER_STRATEGY if FILTER_STRATEGY else 'All strategies'}")
    print()
    
    # Read log file
    records = read_log_file(LOG_PATH)
    if not records:
        print("No records found. Exiting.")
        return
    
    print(f"Loaded {len(records)} records from log file")
    
    # Filter records
    filtered_records = filter_records(records)
    if not filtered_records:
        print("No records to evaluate after filtering. Exiting.")
        return
    
    print(f"Evaluating {len(filtered_records)} records\n")
    
    # Check if we should group by strategy
    strategies = set(r.get('chunking_strategy') for r in filtered_records)
    
    if len(strategies) > 1 and FILTER_STRATEGY is None:
        # Multiple strategies - evaluate separately
        evaluate_by_strategy(filtered_records)
    else:
        # Single strategy or filtered - evaluate all together
        test_cases = create_test_cases(filtered_records)
        metric_scores = evaluate_test_cases(test_cases)
        print_summary(metric_scores, len(filtered_records))
    
    print("Evaluation complete!")


if __name__ == "__main__":
    main()

