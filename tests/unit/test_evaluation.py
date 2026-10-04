from drowsy_preprocessing.evaluation.metrics import evaluate_events


def test_evaluate_needs_ground_truth():
    result = evaluate_events([], None)
    assert result == {"status": "no_ground_truth", "precision": None, "recall": None}


def test_subject_splits_are_disjoint():
    train = {"p1", "p2"}
    test = {"p3"}
    assert train.isdisjoint(test)


def test_temporal_windows_do_not_overlap_across_split():
    train = [(0, 60), (60, 120)]
    test = [(180, 240)]
    assert max(e for _, e in train) <= min(s for s, _ in test)
