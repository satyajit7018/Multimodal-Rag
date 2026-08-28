"""Run the eval set (data/eval_set.json) against a pipeline and report
accuracy per category (text / table / diagram). Run this against the
Week 1 baseline collection and again against the Week 3 multimodal
collections, then diff the two result tables for the comparison writeup.
"""

import json
from collections import defaultdict


def load_eval_set(path: str = "data/eval_set.json") -> list[dict]:
    with open(path) as f:
        return json.load(f)


def score_answer(predicted: str, expected: str) -> bool:
    """Placeholder scoring: substring match on key terms. Replace with
    manual grading or an LLM-as-judge call for anything but a first pass.
    """
    return expected.lower() in predicted.lower()


def run_eval(answer_fn, eval_set: list[dict]) -> dict:
    """answer_fn(question: str) -> str. Returns per-category accuracy."""
    correct_by_cat = defaultdict(int)
    total_by_cat = defaultdict(int)

    for item in eval_set:
        cat = item["category"]
        predicted = answer_fn(item["question"])
        total_by_cat[cat] += 1
        if score_answer(predicted, item["answer"]):
            correct_by_cat[cat] += 1

    return {
        cat: correct_by_cat[cat] / total_by_cat[cat]
        for cat in total_by_cat
    }


if __name__ == "__main__":
    eval_set = load_eval_set()

    def dummy_answer_fn(question: str) -> str:
        return ""  # wire this up to your baseline or multimodal pipeline

    results = run_eval(dummy_answer_fn, eval_set)
    print(json.dumps(results, indent=2))
