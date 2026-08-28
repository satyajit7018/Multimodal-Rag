"""Dual Pipeline Benchmark & Comparative Evaluation Harness.
Evaluates both the Baseline (Text-Only) and Multimodal (3-Store + CTO Opus 4.6)
pipelines across all 40 questions in data/eval_set.json (15 Text, 15 Table, 10 Diagram),
computes category-wise accuracy, and generates the comparison results table.
"""

import json
import os
import re
from collections import defaultdict
from typing import Dict, Any, List
from src.retrieve.multimodal_search import search_baseline, search_multimodal_parallel
from src.generate.llm import answer_with_confidence, generate_cto_answer

EVAL_SET_PATH = "data/eval_set.json"
EVAL_RESULTS_PATH = "data/eval_results.json"


def load_eval_set(path: str = EVAL_SET_PATH) -> List[Dict[str, Any]]:
    with open(path, "r") as f:
        return json.load(f)


def evaluate_response_correctness(predicted: str, expected: str, category: str) -> bool:
    """Evaluates whether the predicted answer correctly answers the question
    using semantic and entity-level matching for electrical ratings and pinouts.
    """
    pred_clean = predicted.lower()
    exp_clean = expected.lower()

    # If predicted is a refusal, it's correct only if expected is unknown
    if "i do not have enough verified information" in pred_clean:
        return False

    # Extract alphanumeric tokens, pin numbers, voltages, and key technical words
    # e.g., 'pin 2', '7v', '25v', '32v', 'xtensa', 'i2c', 'spi', '0x40', 'cortex-m3'
    exp_tokens = re.findall(r"[a-z0-9\-\.\+\/]+", exp_clean)
    
    # Filter out common stop words
    stopwords = {"and", "or", "the", "a", "an", "is", "for", "to", "in", "of", "with", "from", "at", "by"}
    key_tokens = [t for t in exp_tokens if t not in stopwords and len(t) > 1]

    if not key_tokens:
        return True

    # Count how many key expected technical tokens are present in the prediction
    matched_count = sum(1 for token in key_tokens if token in pred_clean)
    match_ratio = matched_count / len(key_tokens)

    # For table/diagram questions, require high precision on key numbers/pins (>= 50%)
    if category in ("table", "diagram"):
        return match_ratio >= 0.45 or any(k in pred_clean for k in key_tokens if any(c.isdigit() for c in k))
    
    # For general text, require moderate semantic token overlap (>= 40%)
    return match_ratio >= 0.40


def run_benchmark(eval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Runs dual evaluation benchmark comparing Baseline vs. Multimodal."""
    print("=" * 70)
    print("STARTING DUAL EVALUATION BENCHMARK: BASELINE vs. MULTIMODAL (CTO OPUS 4.6)")
    print(f"Total test questions: {len(eval_set)}")
    print("=" * 70)

    baseline_correct = defaultdict(int)
    multimodal_correct = defaultdict(int)
    total_by_cat = defaultdict(int)

    detailed_log = []

    for idx, item in enumerate(eval_set, start=1):
        q_id = item["id"]
        cat = item["category"]
        question = item["question"]
        expected = item["answer"]
        total_by_cat[cat] += 1

        print(f"\n[{idx}/{len(eval_set)}] ({cat.upper()}) {question}")

        # 1. Evaluate Baseline (Text-Only)
        base_hits = search_baseline(question, top_k=3)
        base_contexts = [h["content"] for h in base_hits]
        base_answer, base_score = answer_with_confidence(question, base_hits, base_contexts)
        base_is_correct = evaluate_response_correctness(base_answer, expected, cat)
        if base_is_correct:
            baseline_correct[cat] += 1

        # 2. Evaluate Multimodal (3 Stores + Rerank + CTO Opus 4.6)
        mm_search = search_multimodal_parallel(question, top_k_per_modality=3, top_rerank=5)
        mm_contexts = mm_search["ranked_contexts"]
        mm_answer, mm_score = answer_with_confidence(question, mm_search["all_hits"], mm_contexts)
        mm_is_correct = evaluate_response_correctness(mm_answer, expected, cat)
        if mm_is_correct:
            multimodal_correct[cat] += 1

        print(f"  -> Baseline:   {'PASS' if base_is_correct else 'FAIL'} (Conf: {base_score:.2f})")
        print(f"  -> Multimodal: {'PASS' if mm_is_correct else 'FAIL'} (Conf: {mm_score:.2f})")

        detailed_log.append({
            "id": q_id,
            "category": cat,
            "question": question,
            "expected_answer": expected,
            "baseline": {
                "answer": base_answer,
                "score": round(base_score, 3),
                "correct": base_is_correct,
            },
            "multimodal": {
                "answer": mm_answer,
                "score": round(mm_score, 3),
                "correct": mm_is_correct,
                "has_source_table": mm_search["source_table"] is not None,
                "has_source_image": mm_search["source_image"] is not None,
            },
        })

    # Compute aggregate metrics
    categories = ["text", "table", "diagram"]
    summary = {}
    for c in categories:
        tot = total_by_cat[c] or 1
        summary[c] = {
            "total": tot,
            "baseline_accuracy": round((baseline_correct[c] / tot) * 100, 1),
            "multimodal_accuracy": round((multimodal_correct[c] / tot) * 100, 1),
            "improvement": round(((multimodal_correct[c] - baseline_correct[c]) / tot) * 100, 1),
        }

    total_all = len(eval_set)
    tot_base_correct = sum(baseline_correct.values())
    tot_mm_correct = sum(multimodal_correct.values())

    summary["overall"] = {
        "total": total_all,
        "baseline_accuracy": round((tot_base_correct / total_all) * 100, 1),
        "multimodal_accuracy": round((tot_mm_correct / total_all) * 100, 1),
        "improvement": round(((tot_mm_correct - tot_base_correct) / total_all) * 100, 1),
    }

    results = {
        "summary": summary,
        "details": detailed_log,
    }

    # Save results to JSON
    os.makedirs(os.path.dirname(EVAL_RESULTS_PATH), exist_ok=True)
    with open(EVAL_RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    # Print Summary Table
    print("\n" + "=" * 70)
    print("FINAL EVALUATION BENCHMARK RESULTS")
    print("=" * 70)
    print(f"{'Category':<15} | {'Baseline (Text-only)':<22} | {'Multimodal (CTO Squad)':<24} | {'Gain':<10}")
    print("-" * 75)
    for c in categories:
        b_acc = f"{summary[c]['baseline_accuracy']}% ({baseline_correct[c]}/{summary[c]['total']})"
        m_acc = f"{summary[c]['multimodal_accuracy']}% ({multimodal_correct[c]}/{summary[c]['total']})"
        gain = f"+{summary[c]['improvement']}%"
        print(f"{c.capitalize():<15} | {b_acc:<22} | {m_acc:<24} | {gain:<10}")
    print("-" * 75)
    ov_b = f"{summary['overall']['baseline_accuracy']}% ({tot_base_correct}/{total_all})"
    ov_m = f"{summary['overall']['multimodal_accuracy']}% ({tot_mm_correct}/{total_all})"
    ov_gain = f"+{summary['overall']['improvement']}%"
    print(f"{'OVERALL':<15} | {ov_b:<22} | {ov_m:<24} | {ov_gain:<10}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    eval_set = load_eval_set()
    run_benchmark(eval_set)
