"""Структуры данных forecast_comp: запрос и результат прогноза."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .errors import InvalidForecastRequestError, InvalidMlResponseError

#: Максимальный горизонт прогноза (в периодах). Константа учебного прототипа.
MAX_HORIZON: int = 60


class ForecastSource(str, Enum):
    """Откуда получен результат прогноза."""

    CACHE = "cache"
    ML = "ml"


@dataclass(frozen=True, slots=True)
class ForecastRequest:
    """Запрос прогноза: компания и горизонт (число периодов вперёд)."""

    company_id: int
    horizon: int

    def __post_init__(self) -> None:
        if not isinstance(self.company_id, int) or isinstance(self.company_id, bool):
            raise InvalidForecastRequestError("company_id должен быть целым числом")
        if self.company_id <= 0:
            raise InvalidForecastRequestError("company_id должен быть положительным")
        if not isinstance(self.horizon, int) or isinstance(self.horizon, bool):
            raise InvalidForecastRequestError("horizon должен быть целым числом")
        if not 1 <= self.horizon <= MAX_HORIZON:
            raise InvalidForecastRequestError(
                f"horizon должен быть в диапазоне 1..{MAX_HORIZON}, получено {self.horizon}"
            )


@dataclass(frozen=True, slots=True)
class ForecastResult:
    """Результат прогноза: значения, источник и время расчёта."""

    company_id: int
    horizon: int
    values: tuple[float, ...]
    source: ForecastSource
    calculated_at: datetime

    def __post_init__(self) -> None:
        if len(self.values) != self.horizon:
            raise InvalidMlResponseError(
                f"ожидалось {self.horizon} значений прогноза, получено {len(self.values)}"
            )
        if not all(math.isfinite(v) for v in self.values):
            raise InvalidMlResponseError("прогноз содержит NaN или бесконечность")
