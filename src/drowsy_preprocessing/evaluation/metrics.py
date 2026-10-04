from __future__ import annotations


def evaluate_events(predictions, ground_truth):
    if ground_truth is None or len(ground_truth) == 0:
        return {"status": "no_ground_truth", "precision": None, "recall": None}
    p = set(predictions)
    g = set(ground_truth)
    tp = len(p & g)
    return {
        "status": "evaluated",
        "precision": tp / len(p) if p else 0.0,
        "recall": tp / len(g),
    }
