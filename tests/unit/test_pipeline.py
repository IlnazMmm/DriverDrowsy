import json
import math
import pytest

from drowsy_preprocessing.config import Settings
from drowsy_preprocessing.contracts import FrameObservation
from drowsy_preprocessing.signals.events import EventDetector
from drowsy_preprocessing.signals.filtering import CausalMedian
from drowsy_preprocessing.signals.windows import aggregate_window
from drowsy_preprocessing.vision.gaze import gaze_from_68_landmarks
from drowsy_preprocessing.vision.geometry import landmarks68_to_observables


def frames(times, ears, mars=None, session="s"):
    mars = mars or [0.2] * len(times)
    return [
        FrameObservation(session, i, t, e, e, m)
        for i, (t, e, m) in enumerate(zip(times, ears, mars, strict=True))
    ]


def test_manual_perclos_irregular_timestamps():
    fs = frames([0, 0.1, 0.4, 1.0], [0.1, 0.3, 0.1, 0.3])
    w = aggregate_window(fs, [], 0, 1, Settings(maximum_gap_seconds=1))
    assert w.features["perclos"].value == pytest.approx(0.7)


@pytest.mark.parametrize("fps", [15, 30])
def test_fps_duration_uses_timestamps(fps):
    ts = [i / fps for i in range(fps + 1)]
    fs = frames(ts, [0.1 if t < 0.2 else 0.3 for t in ts])
    event = EventDetector(Settings(maximum_gap_seconds=0.2)).run(fs)[0]
    assert 0.18 <= event.duration_s <= 0.27


def test_long_gap_not_extrapolated_and_censors_event():
    fs = frames([0, 0.1, 2, 2.1], [0.1, 0.1, 0.1, 0.3])
    es = EventDetector(Settings()).run(fs)
    assert es[0].censored_end
    assert (
        aggregate_window(fs, es, 0, 2.1, Settings()).features["perclos"].quality < 0.2
    )


def test_one_eye_missing_still_measured_but_no_face_unknown():
    fs = [
        FrameObservation("s", 0, 0, None, 0.1, 0.2),
        FrameObservation("s", 1, 0.1, None, 0.1, 0.2),
    ]
    assert aggregate_window(fs, [], 0, 0.1, Settings()).features["perclos"].value == 1
    noface = [FrameObservation("s", 0, 0), FrameObservation("s", 1, 0.1)]
    assert (
        aggregate_window(noface, [], 0, 0.1, Settings()).features["perclos"].value
        is None
    )


def test_no_iris_means_unknown_gaze():
    assert gaze_from_68_landmarks([[0, 0]] * 68)[0] is None


def test_speech_short_open_not_yawn_candidate_and_long_is_proxy():
    short = frames([0, 0.5, 1], [0.3] * 3, [0.7, 0.7, 0.2])
    assert not [
        e for e in EventDetector(Settings()).run(short) if e.kind == "yawn_candidate"
    ]
    long = frames([0, 1, 2], [0.3] * 3, [0.7, 0.7, 0.2])
    event = [
        e
        for e in EventDetector(Settings(maximum_gap_seconds=1.1)).run(long)
        if e.kind == "yawn_candidate"
    ][0]
    assert event.semantic_level == "proxy"


def test_open_boundary_and_long_closure_are_censored_and_separate():
    es = EventDetector(Settings(maximum_gap_seconds=1)).run(
        frames([0, 0.5, 1], [0.1] * 3)
    )
    assert es[0].kind == "prolonged_closure" and es[0].censored_end


def test_zero_events_rate_but_duration_unknown():
    w = aggregate_window(
        frames([0, 1], [0.3, 0.3]), [], 0, 1, Settings(maximum_gap_seconds=2)
    )
    assert w.features["blink_rate"].value == 0
    assert w.features["blink_duration"].value is None


def test_short_session_is_warmup():
    w = aggregate_window(
        frames([0, 1], [0.3, 0.3]), [], 0, 1, Settings(maximum_gap_seconds=2)
    )
    assert w.warmup


@pytest.mark.parametrize("times", [[0, 0], [1, 0]])
def test_timestamp_repeat_or_regression_rejected(times):
    with pytest.raises(ValueError):
        aggregate_window(frames(times, [0.3, 0.3]), [], 0, 1, Settings())


def test_incompatible_landmarks():
    with pytest.raises(ValueError):
        landmarks68_to_observables([[0, 0]] * 67)


def test_sessions_not_joined_by_event_detector():
    fs = frames([0, 0.1], [0.1, 0.1], session="a") + frames(
        [0.2, 0.3], [0.1, 0.3], session="b"
    )
    with pytest.raises(ValueError):
        EventDetector(Settings()).run(fs)


def test_sliding_windows_does_not_create_zero_length_window():
    from drowsy_preprocessing.signals.windows import sliding_windows

    result = sliding_windows(
        frames([0, 1], [0.3, 0.3]), [], Settings(maximum_gap_seconds=2)
    )
    assert len(result) == 1 and result[0].end_s > result[0].start_s


def test_filter_has_no_future_leak_and_is_repeatable():
    a = CausalMedian()
    first = a.update(1)
    a.update(100)
    b = CausalMedian()
    assert first == b.update(1) == 1


def test_json_forbids_nonfinite():
    w = aggregate_window(
        frames([0, 1], [0.3, 0.3]), [], 0, 1, Settings(maximum_gap_seconds=2)
    )
    json.loads(w.to_json())
    object.__setattr__(w.features["blink_rate"], "value", math.inf)
    with pytest.raises(ValueError):
        w.to_json()
