from __future__ import annotations

from drowsy_preprocessing.config import Settings
from drowsy_preprocessing.contracts import (
    Event,
    FEATURE_NAMES,
    FeatureValue,
    FeatureWindow,
    FrameObservation,
)


def _overlap(a: float, b: float, c: float, d: float) -> float:
    return max(0.0, min(b, d) - max(a, c))


def aggregate_window(
    frames: list[FrameObservation],
    events: list[Event],
    start: float,
    end: float,
    settings: Settings,
) -> FeatureWindow:
    if end <= start:
        raise ValueError("invalid window")
    selected = [f for f in frames if start <= f.timestamp_s <= end]
    session = (
        selected[0].session_id
        if selected
        else (frames[0].session_id if frames else "unknown")
    )
    eye_known = 0.0
    eye_closed = 0.0
    # Left-closed intervals avoid assuming state past gaps or missing endpoints.
    for a, b in zip(selected, selected[1:]):
        dt = b.timestamp_s - a.timestamp_s
        if dt <= 0:
            raise ValueError("timestamps must be strictly increasing")
        if dt > settings.maximum_gap_seconds:
            continue
        vals = [x for x in (a.left_ear, a.right_ear) if x is not None]
        if not vals:
            continue
        covered = _overlap(a.timestamp_s, b.timestamp_s, start, end)
        eye_known += covered
        if sum(vals) / len(vals) <= settings.ear_close_threshold:
            eye_closed += covered
    eye_quality = eye_known / (end - start)
    perclos = (
        FeatureValue(
            eye_closed / eye_known, "fraction", "measured", quality=eye_quality
        )
        if eye_known
        else FeatureValue(None, "fraction", "unknown", "no_valid_eye_duration", 0.0)
    )
    complete_blinks = [
        e
        for e in events
        if e.kind == "blink"
        and not e.censored_start
        and not e.censored_end
        and start <= e.start_s
        and e.end_s <= end
    ]
    blink_rate = (
        FeatureValue(
            len(complete_blinks) * 60 / (end - start),
            "events/min",
            "measured",
            quality=eye_quality,
        )
        if eye_known
        else FeatureValue(None, "events/min", "unknown", "no_valid_eye_duration", 0.0)
    )
    blink_duration = (
        FeatureValue(
            sum(e.duration_s for e in complete_blinks) / len(complete_blinks),
            "s",
            "measured",
            quality=eye_quality,
        )
        if complete_blinks
        else (
            FeatureValue(None, "s", "unknown", "no_complete_blink_events", eye_quality)
        )
    )
    gaze_values = [f.gaze for f in selected if f.gaze is not None]
    gaze = FeatureValue(
        None,
        "normalized_xy",
        "unknown",
        "gaze_backend_unavailable_or_missing_iris",
        0.0,
    )
    if gaze_values:
        gaze = FeatureValue(
            {
                "x": sum(x[0] for x in gaze_values) / len(gaze_values),
                "y": sum(x[1] for x in gaze_values) / len(gaze_values),
            },
            "normalized_xy",
            "measured",
            quality=sum((f.gaze_quality or 0) for f in selected if f.gaze is not None)
            / len(gaze_values),
        )
    mouth_known = sum(
        max(0.0, b.timestamp_s - a.timestamp_s)
        for a, b in zip(selected, selected[1:])
        if a.mar is not None
        and b.timestamp_s - a.timestamp_s <= settings.maximum_gap_seconds
    )
    yc = [
        e
        for e in events
        if e.kind == "yawn_candidate"
        and not e.censored_start
        and not e.censored_end
        and start <= e.start_s
        and e.end_s <= end
    ]
    mq = mouth_known / (end - start)
    yd = (
        FeatureValue(sum(e.duration_s for e in yc) / len(yc), "s", "proxy", quality=mq)
        if yc
        else (
            FeatureValue(
                None,
                "s",
                "unknown",
                (
                    "no_complete_yawn_candidate_events"
                    if mouth_known
                    else "no_valid_mouth_duration"
                ),
                mq,
            )
        )
    )
    yr = (
        FeatureValue(len(yc) * 60 / (end - start), "events/min", "proxy", quality=mq)
        if mouth_known
        else FeatureValue(None, "events/min", "unknown", "no_valid_mouth_duration", 0.0)
    )
    features = dict(
        zip(
            FEATURE_NAMES,
            (perclos, blink_rate, blink_duration, gaze, yd, yr),
            strict=True,
        )
    )
    return FeatureWindow(
        settings.schema_version,
        session,
        start,
        end,
        end - start < settings.production_window_seconds,
        features,
        settings.hash,
    )


def sliding_windows(
    frames: list[FrameObservation],
    events: list[Event],
    settings: Settings,
    width: float | None = None,
):
    if not frames:
        return []
    width = width or settings.production_window_seconds
    first, last = frames[0].timestamp_s, frames[-1].timestamp_s
    out = []
    end = first + settings.step_seconds
    while end <= last + 1e-9:
        out.append(
            aggregate_window(frames, events, max(first, end - width), end, settings)
        )
        end += settings.step_seconds
    return out
