from __future__ import annotations


class GazeBackend:
    def estimate(self, *, iris_features=None):
        if iris_features is None:
            return None, "iris_or_validated_estimator_unavailable"
        raise NotImplementedError("configure a validated gaze estimator")


def gaze_from_68_landmarks(_points):
    return None, "landmarks_68_do_not_contain_pupil_or_iris"
