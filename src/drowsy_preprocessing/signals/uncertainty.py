def sensitivity_range(values: list[float]) -> dict[str, float] | None:
    """Range under configured perturbations; neither FOU nor confidence interval."""
    return {"minimum": min(values), "maximum": max(values)} if values else None
