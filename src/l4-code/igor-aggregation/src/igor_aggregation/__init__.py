"""L4 prototype for dwh / dwh_query_comp."""

from .models import FinancialTimeSeries
from .service import FinancialQueryService
from .strategies import (
    AggregationStrategy,
    AverageAggregation,
    MaxAggregation,
    SumAggregation,
)

__all__ = [
    "AggregationStrategy", "AverageAggregation", "FinancialQueryService",
    "FinancialTimeSeries", "MaxAggregation", "SumAggregation",
]
