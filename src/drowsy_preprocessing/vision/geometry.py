from __future__ import annotations

import math
from collections.abc import Sequence

Point = Sequence[float]


def _distance(a: Point, b: Point) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def eye_aspect_ratio(points: Sequence[Point]) -> float:
    """Geometric landmark ratio (not a physical eyelid-closure fraction)."""
    if len(points) != 6:
        raise ValueError("EAR requires exactly 6 eye landmarks")
    width = 2.0 * _distance(points[0], points[3])
    if width == 0:
        raise ValueError("degenerate eye landmarks")
    return (_distance(points[1], points[5]) + _distance(points[2], points[4])) / width


def mouth_aspect_ratio(points: Sequence[Point]) -> float:
    if len(points) != 8:
        raise ValueError("MAR requires exactly 8 inner-mouth landmarks")
    width = 2.0 * _distance(points[0], points[4])
    if width == 0:
        raise ValueError("degenerate mouth landmarks")
    return (
        _distance(points[1], points[7])
        + _distance(points[2], points[6])
        + _distance(points[3], points[5])
    ) / width


def landmarks68_to_observables(points: Sequence[Point]) -> tuple[float, float, float]:
    if len(points) != 68:
        raise ValueError(f"expected 68 landmarks, got {len(points)}")
    return (
        eye_aspect_ratio(points[36:42]),
        eye_aspect_ratio(points[42:48]),
        mouth_aspect_ratio(points[60:68]),
    )
