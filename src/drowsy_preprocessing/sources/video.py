from drowsy_preprocessing.vision.base import LandmarkBackend


class VideoSource:
    """Optional frame source. OpenCV import is deferred for dataset-only workflows."""

    def __init__(self, backend: LandmarkBackend):
        self.backend = backend

    def open(self, path: str):
        import cv2

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError(f"cannot open video: {path}")
        return cap
