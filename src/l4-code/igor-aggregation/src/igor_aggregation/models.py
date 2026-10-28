"""Immutable, non-empty series of finite numeric observations."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class FinancialTimeSeries:
    """Values already selected for one metric, company, period and currency.

    Ordering is preserved; timestamps and database selection are outside L4.
    bool, strings, None, NaN and infinity are not numeric observations here.
    """

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("Time series must not be empty")
        normalized: list[float] = []
        for value in self.values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("Each observation must be an int or float, not bool")
            number = float(value)
            if not isfinite(number):
                raise ValueError("Each observation must be finite")
            normalized.append(number)
        object.__setattr__(self, "values", tuple(normalized))
