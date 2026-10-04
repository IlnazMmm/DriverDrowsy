from __future__ import annotations


class CausalMedian:
    def __init__(self, size: int = 3):
        if size < 1:
            raise ValueError("size must be positive")
        self.size, self._past = size, []

    def update(self, value: float | None) -> float | None:
        if value is None:
            return None
        self._past.append(value)
        self._past = self._past[-self.size :]
        values = sorted(self._past)
        return values[len(values) // 2]
