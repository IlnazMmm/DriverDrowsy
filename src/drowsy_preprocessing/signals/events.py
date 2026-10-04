from __future__ import annotations

from dataclasses import dataclass
from drowsy_preprocessing.contracts import Event, FrameObservation
from drowsy_preprocessing.config import Settings


@dataclass
class _Open:
    kind: str
    start: float
    censored_start: bool = False


class EventDetector:
    """Causal hysteresis; gaps censor and terminate rather than bridge events."""

    def __init__(self, settings: Settings):
        self.s = settings

    def run(self, frames: list[FrameObservation]) -> list[Event]:
        if not frames:
            return []
        if any(frame.session_id != frames[0].session_id for frame in frames):
            raise ValueError("events cannot cross session boundaries")
        out: list[Event] = []
        eye: _Open | None = None
        mouth: _Open | None = None
        last_t: float | None = None
        for frame in frames:
            t = frame.timestamp_s
            if last_t is not None:
                if t <= last_t:
                    raise ValueError("timestamps must be strictly increasing")
                if t - last_t > self.s.maximum_gap_seconds:
                    if eye:
                        out.append(self._finish(frame.session_id, eye, last_t, True))
                    if mouth:
                        out.append(self._finish(frame.session_id, mouth, last_t, True))
                    eye = mouth = None
            ear_values = [x for x in (frame.left_ear, frame.right_ear) if x is not None]
            ear = sum(ear_values) / len(ear_values) if ear_values else None
            if ear is None:
                if eye:
                    out.append(self._finish(frame.session_id, eye, last_t or t, True))
                    eye = None
            elif eye is None and ear <= self.s.ear_close_threshold:
                eye = _Open("closure", t)
            elif eye is not None and ear >= self.s.ear_open_threshold:
                duration = t - eye.start
                kind = (
                    "blink"
                    if duration <= self.s.maximum_blink_seconds
                    else "prolonged_closure"
                )
                if duration >= self.s.minimum_blink_seconds:
                    out.append(Event(frame.session_id, kind, eye.start, t, duration))
                eye = None
            if frame.mar is None:
                if mouth:
                    out.append(self._finish(frame.session_id, mouth, last_t or t, True))
                    mouth = None
            elif mouth is None and frame.mar >= self.s.mar_open_threshold:
                mouth = _Open("yawn_candidate", t)
            elif mouth is not None and frame.mar <= self.s.mar_close_threshold:
                e = self._finish(frame.session_id, mouth, t, False)
                if e.duration_s >= self.s.minimum_yawn_candidate_seconds:
                    out.append(e)
                mouth = None
            last_t = t
        if eye:
            out.append(
                self._finish(frames[-1].session_id, eye, frames[-1].timestamp_s, True)
            )
        if mouth:
            out.append(
                self._finish(frames[-1].session_id, mouth, frames[-1].timestamp_s, True)
            )
        return out

    @staticmethod
    def _finish(session: str, opened: _Open, end: float, censored: bool) -> Event:
        kind = opened.kind
        if kind == "closure":
            kind = "prolonged_closure"
        return Event(
            session,
            kind,
            opened.start,
            end,
            max(0.0, end - opened.start),
            opened.censored_start,
            censored,
            "proxy" if kind == "yawn_candidate" else "measured",
        )
