from dataclasses import dataclass


@dataclass(frozen=True)
class Normalization:
    mean: float
    scale: float
    split: str = "train"

    def apply(self, value: float) -> float:
        if self.split != "train":
            raise ValueError("normalization parameters must be fitted on train")
        if self.scale <= 0:
            raise ValueError("scale must be positive")
        return (value - self.mean) / self.scale
