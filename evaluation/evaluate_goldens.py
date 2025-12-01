"""
Golden Dataset Evaluation Script (Reference-Based Metrics).

Evaluates RAG app performance using a golden dataset with ground truth answers.
Queries the running RAG API and compares actual responses against expected outputs.

Metrics:
- Contextual Precision: Whether relevant chunks are ranked higher in retrieval
- Contextual Recall: Whether retrieved context contains the expected answer

Requires:
- Backend server running (python run_server.py)
- Golden dataset JSON file with expected_output and context fields
"""

import json
import requests
import argparse
from collections import defaultdict
from statistics import mean, stdev
from typing import List, Dict, Any

from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)

# Configuration constants
DEFAULT_GOLDENS_PATH = "TestNotebooks/synthetic_data/my_dataset.json"
API_URL = "http://localhost:8000/api/chat"  # RAG API endpoint

# Ollama configuration for evaluation
OLLAMA_MODEL = "qwen3:0.6b"
OLLAMA_BASE_URL = "http://localhost:11434"


def load_goldens(goldens_path: str) -> List[Dict[str, Any]]:
    """Load golden dataset from JSON file.
    
    Args:
        goldens_path: Path to the golden dataset JSON file
        
    Returns:
        List of golden test cases
    """
    try:
        with open(goldens_path, 'r', encoding='utf-8') as f:
            goldens = json.load(f)
        return goldens
    except FileNotFoundError:
        print(f"Error: Golden dataset not found at {goldens_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in golden dataset: {e}")
        return []


def query_rag_api(question: str) -> tuple[str, List[str]]:
    """Query the RAG API and extract answer and retrieved context.
    
    Args:
        question: User question to send to the API
        
    Returns:
        Tuple of (answer, retrieved_context_list)
        
    Raises:
        Exception: If API call fails
    """
    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract answer
        answer = data.get("answer", "")
        
        # Extract retrieved context from sources
        sources = data.get("sources", [])
        retrieved_context = [s.get("content", "") for s in sources if s.get("content")]
        
        return answer, retrieved_context
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")


def create_test_case(golden: Dict[str, Any], actual_answer: str, retrieved_context: List[str]) -> LLMTestCase:
    """Create a DeepEval test case from golden data and API response.
    
    Args:
        golden: Golden dataset entry with input, expected_output, and context
        actual_answer: Answer from RAG API
        retrieved_context: Context retrieved by RAG API
        
    Returns:
        LLMTestCase object
    """
    return LLMTestCase(
        input=golden.get("input", ""),
        actual_output=actual_answer,
        expected_output=golden.get("expected_output", ""),
        retrieval_context=retrieved_context,
        context=golden.get("context", [])  # Expected context from golden
    )


def evaluate_test_cases(test_cases: List[LLMTestCase]) -> Dict[str, List[float]]:
    """Evaluate test cases using DeepEval metrics with Ollama.
    
    Args:
        test_cases: List of LLMTestCase objects
        
    Returns:
        Dictionary mapping metric names to lists of scores
    """
    # Initialize Ollama model once for reuse
    ollama_model = OllamaModel(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0
    )
    
    # Create metric instances
    metrics = {
        "ContextualPrecisionMetric": ContextualPrecisionMetric(model=ollama_model),
        "ContextualRecallMetric": ContextualRecallMetric(model=ollama_model),
    }
    
    # Store scores for each metric
    metric_scores = defaultdict(list)
    
    # Evaluate each test case with each metric
    print(f"Evaluating test cases using Ollama model: {OLLAMA_MODEL}...")
    for i, test_case in enumerate(test_cases):
        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1}/{len(test_cases)} test cases...")
        
        for metric_name, metric in metrics.items():
            try:
                metric.measure(test_case)
                score = metric.score
                if score is not None:
                    metric_scores[metric_name].append(score)
            except Exception as e:
                print(f"  Warning: Failed to evaluate {metric_name} for test case {i+1}: {e}")
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


def print_summary(metric_scores: Dict[str, List[float]], num_records: int):
    """Print evaluation summary statistics.
    
    Args:
        metric_scores: Dictionary mapping metric names to lists of scores
        num_records: Number of records evaluated
    """
    print(f"\n{'='*60}")
    print("Golden Dataset Evaluation Summary")
    print(f"{'='*60}")
    print(f"Total test cases evaluated: {num_records}\n")
    
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


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(
        description="Evaluate RAG app using golden dataset (Reference-Based Metrics)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evaluate_goldens.py
  python evaluate_goldens.py --goldens path/to/goldens.json
        """
    )
    parser.add_argument(
        "--goldens",
        default=DEFAULT_GOLDENS_PATH,
        help=f"Path to golden dataset JSON file (default: {DEFAULT_GOLDENS_PATH})"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Golden Dataset Evaluation (Reference-Based Metrics)")
    print("=" * 60)
    print(f"Golden dataset: {args.goldens}")
    print(f"API URL: {API_URL}")
    print(f"Evaluation model: {OLLAMA_MODEL}")
    print()
    
    # Load golden dataset
    goldens = load_goldens(args.goldens)
    if not goldens:
        print("No golden test cases found. Exiting.")
        return
    
    print(f"Loaded {len(goldens)} golden test cases")
    print("Querying RAG API for each test case...\n")
    
    # Query API and create test cases
    test_cases = []
    failed_queries = 0
    
    for i, golden in enumerate(goldens):
        question = golden.get("input", "")
        if not question:
            print(f"  Warning: Skipping golden {i+1} - missing 'input' field")
            continue
        
        try:
            print(f"  [{i+1}/{len(goldens)}] Querying: {question[:60]}...")
            actual_answer, retrieved_context = query_rag_api(question)
            
            # Create test case
            test_case = create_test_case(golden, actual_answer, retrieved_context)
            test_cases.append(test_case)
            
        except Exception as e:
            print(f"  ✗ Failed to query API for golden {i+1}: {e}")
            failed_queries += 1
            continue
    
    if not test_cases:
        print("\nNo test cases created. Cannot proceed with evaluation.")
        if failed_queries > 0:
            print(f"Failed to query API for {failed_queries} test case(s).")
            print("Make sure your backend server is running: python run_server.py")
        return
    
    print(f"\nSuccessfully created {len(test_cases)} test cases")
    if failed_queries > 0:
        print(f"Warning: {failed_queries} test case(s) failed to query API")
    print()
    
    # Evaluate test cases
    metric_scores = evaluate_test_cases(test_cases)
    
    # Print summary
    print_summary(metric_scores, len(test_cases))
    
    print("Evaluation complete!")


if __name__ == "__main__":
    main()

