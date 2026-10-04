from __future__ import annotations
from typing import Protocol, Sequence


class LandmarkBackend(Protocol):
    model_hash: str

    def detect(self, frame: object) -> Sequence[Sequence[float]] | None: ...


class UnavailableLandmarkBackend:
    model_hash = "unavailable"

    def detect(self, frame: object):
        raise RuntimeError(
            "No landmark weights are configured; live/video detection is unavailable"
        )
