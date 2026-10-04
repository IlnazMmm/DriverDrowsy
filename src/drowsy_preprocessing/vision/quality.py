def roi_quality(
    *, detected: bool, in_frame_fraction: float, sharpness: float | None
) -> float | None:
    if not detected or sharpness is None:
        return None
    return max(0.0, min(1.0, in_frame_fraction)) * max(0.0, min(1.0, sharpness))
