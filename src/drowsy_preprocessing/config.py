from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    schema_version: str = "1.0.0"
    drozy_root: str | None = None
    window_seconds: list[float] = field(default_factory=lambda: [30.0, 60.0, 120.0])
    production_window_seconds: float = 60.0
    step_seconds: float = 1.0
    maximum_gap_seconds: float = 0.5
    ear_close_threshold: float = 0.20
    ear_open_threshold: float = 0.24
    mar_open_threshold: float = 0.60
    mar_close_threshold: float = 0.50
    minimum_blink_seconds: float = 0.08
    maximum_blink_seconds: float = 0.8
    minimum_yawn_candidate_seconds: float = 1.5
    interp_indices_semantics: str | None = None

    @classmethod
    def load(cls, path: str | Path) -> "Settings":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))

    @property
    def hash(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()
