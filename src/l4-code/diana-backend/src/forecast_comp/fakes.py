"""Имитаторы зависимостей для демонстрации и тестов.

ВНИМАНИЕ: это заглушки, а не настоящие db_repo_comp и ml_client_comp.
Настоящий ML-сервис здесь не вызывается, значения прогноза — тестовые.
"""

from __future__ import annotations

from typing import Optional, Sequence

from .errors import MlServiceUnavailableError
from .models import ForecastResult


class InMemoryForecastCache:
    """Кэш прогнозов в памяти (имитация db_repo_comp)."""

    def __init__(self) -> None:
        self._items: dict[tuple[int, int], ForecastResult] = {}

    def get(self, company_id: int, horizon: int) -> Optional[ForecastResult]:
        return self._items.get((company_id, horizon))

    def put(self, result: ForecastResult) -> None:
        self._items[(result.company_id, result.horizon)] = result


class FakeMlClient:
    """Имитация ml_client_comp: линейный тестовый ряд либо «сервис недоступен»."""

    def __init__(self, base: float = 100.0, step: float = 10.0, available: bool = True) -> None:
        self.base = base
        self.step = step
        self.available = available
        self.calls: int = 0

    def predict(self, company_id: int, horizon: int) -> Sequence[float]:
        self.calls += 1
        if not self.available:
            raise MlServiceUnavailableError("ML-сервис недоступен (имитация)")
        return [self.base + self.step * i for i in range(1, horizon + 1)]
