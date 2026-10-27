"""Стратегии получения прогноза (паттерн Strategy) для forecast_comp."""

from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Callable, Optional

from .errors import CacheMissError, MlServiceUnavailableError
from .models import ForecastRequest, ForecastResult, ForecastSource
from .ports import ForecastCacheReader, ForecastCacheWriter, MlClient

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    """Текущее время в UTC (подменяется в тестах)."""
    return datetime.now(timezone.utc)


class ForecastRetrievalStrategy(ABC):
    """Единый контракт: как получить прогноз для запроса."""

    @abstractmethod
    def execute(self, request: ForecastRequest) -> ForecastResult:
        """Вернуть прогноз или бросить ForecastError."""


class CachedForecastStrategy(ForecastRetrievalStrategy):
    """Берёт ранее сохранённый прогноз из кэша (db_repo_comp)."""

    def __init__(self, cache: ForecastCacheReader) -> None:
        self._cache = cache

    def execute(self, request: ForecastRequest) -> ForecastResult:
        stored = self._cache.get(request.company_id, request.horizon)
        if stored is None:
            raise CacheMissError(
                f"нет сохранённого прогноза: company_id={request.company_id}, "
                f"horizon={request.horizon}"
            )
        # Время расчёта остаётся исходным, источник отражает фактический путь получения.
        return dataclasses.replace(stored, source=ForecastSource.CACHE)


class MlForecastStrategy(ForecastRetrievalStrategy):
    """Запрашивает новый расчёт у ML-сервиса через ml_client_comp."""

    def __init__(
        self,
        ml_client: MlClient,
        writer: Optional[ForecastCacheWriter] = None,
        clock: Clock = utc_now,
    ) -> None:
        self._ml_client = ml_client
        self._writer = writer
        self._clock = clock

    def execute(self, request: ForecastRequest) -> ForecastResult:
        raw = self._ml_client.predict(request.company_id, request.horizon)
        # ForecastResult проверяет длину и конечность значений (InvalidMlResponseError).
        result = ForecastResult(
            company_id=request.company_id,
            horizon=request.horizon,
            values=tuple(float(v) for v in raw),
            source=ForecastSource.ML,
            calculated_at=self._clock(),
        )
        if self._writer is not None:
            self._writer.put(result)
        return result


class FallbackForecastStrategy(ForecastRetrievalStrategy):
    """Сначала primary (обычно ML); при недоступности ML — fallback (обычно кэш).

    Реализует поведение из L3: «при недоступности ML-сервиса отдаёт последний
    сохранённый прогноз». Другие ошибки (например, неверный ответ ML) не
    маскируются и пробрасываются вызывающему.
    """

    def __init__(
        self, primary: ForecastRetrievalStrategy, fallback: ForecastRetrievalStrategy
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    def execute(self, request: ForecastRequest) -> ForecastResult:
        try:
            return self._primary.execute(request)
        except MlServiceUnavailableError:
            return self._fallback.execute(request)
