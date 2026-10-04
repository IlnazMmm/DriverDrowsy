from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from drowsy_preprocessing.config import Settings
from drowsy_preprocessing.contracts import FrameObservation
from drowsy_preprocessing.vision.geometry import landmarks68_to_observables


@dataclass(frozen=True)
class ManifestEntry:
    session_id: str
    subject_id: str
    timestamps: Path
    landmarks: Path
    interp_indices: Path | None = None
    video: Path | None = None
    kss: str | None = None


def read_manifest(path: str | Path) -> list[ManifestEntry]:
    base = Path(path).resolve().parent
    result = []
    with Path(path).open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):

            def p(name):
                return (base / row[name]).resolve() if row.get(name) else None

            result.append(
                ManifestEntry(
                    row["session_id"],
                    row["subject_id"],
                    p("timestamps"),
                    p("landmarks"),
                    p("interp_indices"),
                    p("video"),
                    row.get("kss") or None,
                )
            )
    return result


def _rows(path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


class DrozySource:
    def __init__(self, settings: Settings):
        self.settings = settings

    def audit(self, entry: ManifestEntry) -> dict:
        ts = _rows(entry.timestamps)
        lm = _rows(entry.landmarks)
        report = {
            "session_id": entry.session_id,
            "timestamps_count": len(ts),
            "landmarks_count": len(lm),
            "files_read_only": True,
            "kss_present": entry.kss is not None,
        }
        report["lengths_match"] = len(ts) == len(lm)
        if not report["lengths_match"]:
            report["blocking_error"] = (
                "timestamps and landmarks lengths differ; explicit alignment is required"
            )
        if entry.interp_indices:
            report["interp_indices_count"] = len(_rows(entry.interp_indices))
            if self.settings.interp_indices_semantics not in {
                "zero_based_interpolated_frames",
                "one_based_interpolated_frames",
            }:
                report["blocking_error"] = (
                    "interpIndices semantics are unconfirmed; set interp_indices_semantics after README/code/manual verification"
                )
        values = [float(r[0] if isinstance(r, list) else r) for r in ts]
        report["strictly_increasing"] = all(b > a for a, b in zip(values, values[1:]))
        report["fps_median_estimate"] = (
            1 / statistics.median(b - a for a, b in zip(values, values[1:]))
            if len(values) > 1
            else None
        )
        return report

    def load(self, entry: ManifestEntry) -> list[FrameObservation]:
        audit = self.audit(entry)
        if audit.get("blocking_error"):
            raise ValueError(audit["blocking_error"])
        if not audit["strictly_increasing"]:
            raise ValueError("timestamp repeat or regression")
        timestamps = _rows(entry.timestamps)
        landmarks = _rows(entry.landmarks)
        interp = set()
        if entry.interp_indices:
            offset = (
                0 if self.settings.interp_indices_semantics.startswith("zero") else 1
            )
            interp = {
                int((r[0] if isinstance(r, list) else r)) - offset
                for r in _rows(entry.interp_indices)
            }
        frames = []
        for i, (tr, points) in enumerate(zip(timestamps, landmarks, strict=True)):
            t = float(tr[0] if isinstance(tr, list) else tr)
            try:
                if len(points) == 136 and not isinstance(points[0], (list, tuple)):
                    numeric = [float(value) for value in points]
                    points = list(zip(numeric[::2], numeric[1::2], strict=True))
                left, right, mar = landmarks68_to_observables(points)
            except (TypeError, ValueError):
                left = right = mar = None
            reason = (
                {}
                if left is not None
                else {
                    "eyes": "missing_or_incompatible_landmarks",
                    "mouth": "missing_or_incompatible_landmarks",
                    "gaze": "68_landmarks_have_no_iris",
                }
            )
            frames.append(
                FrameObservation(
                    entry.session_id,
                    i,
                    t,
                    left,
                    right,
                    mar,
                    None,
                    1.0 if left is not None else None,
                    1.0 if mar is not None else None,
                    None,
                    "interpolated" if i in interp else "observed",
                    reason,
                )
            )
        return frames
