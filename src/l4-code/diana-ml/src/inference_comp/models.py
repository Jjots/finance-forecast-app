"""Структуры данных inference_comp: временной ряд и результат прогноза."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .errors import InvalidHorizonError, InvalidTimeSeriesError

#: Максимальный горизонт прогноза (в периодах). Константа учебного прототипа.
MAX_HORIZON: int = 60


def validate_horizon(horizon: int) -> int:
    """Проверить горизонт прогноза и вернуть его."""
    if not isinstance(horizon, int) or isinstance(horizon, bool):
        raise InvalidHorizonError("horizon должен быть целым числом")
    if not 1 <= horizon <= MAX_HORIZON:
        raise InvalidHorizonError(
            f"horizon должен быть в диапазоне 1..{MAX_HORIZON}, получено {horizon}"
        )
    return horizon


@dataclass(frozen=True, slots=True)
class TimeSeriesData:
    """Исторические значения финансового показателя в хронологическом порядке."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        try:
            coerced = tuple(float(v) for v in self.values)
        except (TypeError, ValueError) as exc:
            raise InvalidTimeSeriesError("значения ряда должны быть числами") from exc
        if not coerced:
            raise InvalidTimeSeriesError("временной ряд пуст")
        if not all(math.isfinite(v) for v in coerced):
            raise InvalidTimeSeriesError("ряд содержит NaN или бесконечность")
        object.__setattr__(self, "values", coerced)

    @classmethod
    def from_sequence(cls, values: Sequence[float]) -> "TimeSeriesData":
        """Удобный конструктор из любой последовательности чисел."""
        return cls(values=tuple(values))

    def __len__(self) -> int:
        return len(self.values)


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """Результат прогноза: горизонт, значения и имя использованной модели."""

    horizon: int
    values: tuple[float, ...]
    model_name: str

    def __post_init__(self) -> None:
        validate_horizon(self.horizon)
        if len(self.values) != self.horizon:
            raise InvalidHorizonError(
                f"ожидалось {self.horizon} значений, получено {len(self.values)}"
            )
        if not all(math.isfinite(v) for v in self.values):
            raise InvalidTimeSeriesError("прогноз содержит NaN или бесконечность")
