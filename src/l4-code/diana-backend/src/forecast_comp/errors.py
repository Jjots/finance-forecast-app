"""Исключения компонента forecast_comp (backend)."""

from __future__ import annotations


class ForecastError(Exception):
    """Базовая ошибка получения прогноза."""


class InvalidForecastRequestError(ForecastError, ValueError):
    """Некорректные параметры запроса (company_id, horizon)."""


class CacheMissError(ForecastError):
    """В хранилище нет сохранённого прогноза для запроса."""


class MlServiceUnavailableError(ForecastError):
    """ML-сервис недоступен (таймаут, сеть, открытый circuit breaker)."""


class InvalidMlResponseError(ForecastError):
    """ML-сервис вернул ответ, не соответствующий контракту."""
