"""Context: validate input once and delegate through the Strategy contract."""

from collections.abc import Sequence

from .models import FinancialTimeSeries
from .strategies import AggregationStrategy


class FinancialQueryService:
    """A synchronous local prototype, not a SQL connection or HTTP service."""

    def __init__(self, strategy: AggregationStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: AggregationStrategy) -> None:
        """Replace the algorithm for subsequent calls on this context."""
        self._strategy = strategy

    def execute(self, values: Sequence[float]) -> float:
        """Snapshot and validate values; propagate explicit domain errors."""
        series = FinancialTimeSeries(tuple(values))
        return self._strategy.execute(series)
