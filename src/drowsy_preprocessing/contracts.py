from __future__ import annotations

import dataclasses
import json
import math
from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["measured", "proxy", "unknown"]


@dataclass(frozen=True)
class FrameObservation:
    session_id: str
    frame_index: int
    timestamp_s: float
    left_ear: float | None = None
    right_ear: float | None = None
    mar: float | None = None
    gaze: tuple[float, float] | None = None
    eye_quality: float | None = None
    mouth_quality: float | None = None
    gaze_quality: float | None = None
    timestamp_status: Literal["observed", "interpolated", "repeated"] = "observed"
    missing_reasons: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Event:
    session_id: str
    kind: Literal["blink", "prolonged_closure", "yawn_candidate"]
    start_s: float
    end_s: float
    duration_s: float
    censored_start: bool = False
    censored_end: bool = False
    semantic_level: Literal["measured", "proxy"] = "measured"


@dataclass(frozen=True)
class FeatureValue:
    value: float | dict[str, float] | None
    unit: str
    status: Status
    reason: str | None = None
    quality: float | None = None

    def __post_init__(self) -> None:
        if self.value is None and not self.reason:
            raise ValueError("null feature requires reason")
        if self.value is not None and self.status == "unknown":
            raise ValueError("unknown feature must be null")


@dataclass(frozen=True)
class FeatureWindow:
    schema_version: str
    session_id: str
    start_s: float
    end_s: float
    warmup: bool
    features: dict[str, FeatureValue]
    config_hash: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        def reject(value: Any) -> None:
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("JSON contract forbids NaN/Infinity")
            if isinstance(value, dict):
                for item in value.values():
                    reject(item)
            if isinstance(value, (list, tuple)):
                for item in value:
                    reject(item)

        result = self.to_dict()
        reject(result)
        return json.dumps(result, allow_nan=False, sort_keys=True)


FEATURE_NAMES = (
    "perclos",
    "blink_rate",
    "blink_duration",
    "gaze_direction",
    "yawn_duration",
    "yawn_rate",
)
