"""Interchangeable, stateless aggregation algorithms."""

from math import fsum, isfinite
from typing import Protocol

from .models import FinancialTimeSeries


class AggregationStrategy(Protocol):
    """Return a finite float; reject unrepresentable results with OverflowError."""

    def execute(self, series: FinancialTimeSeries) -> float:
        """Aggregate a validated, immutable series without changing it."""
        ...


class SumAggregation:
    """Accurate floating-point summation; O(n) time."""

    def execute(self, series: FinancialTimeSeries) -> float:
        result = fsum(series.values)
        if not isfinite(result):
            raise OverflowError("Sum is outside the finite float range")
        return result


class AverageAggregation:
    """Arithmetic mean with scaling to avoid overflowing a finite mean."""

    def execute(self, series: FinancialTimeSeries) -> float:
        scale = max(abs(value) for value in series.values)
        if scale == 0.0:
            return 0.0
        mean = fsum(value / scale for value in series.values) / len(series.values)
        # A mean of finite values cannot exceed their maximum magnitude.
        return max(-1.0, min(1.0, mean)) * scale


class MaxAggregation:
    """Largest observation, including in entirely negative series."""

    def execute(self, series: FinancialTimeSeries) -> float:
        return max(series.values)
