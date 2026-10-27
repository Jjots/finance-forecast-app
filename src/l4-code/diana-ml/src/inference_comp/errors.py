"""Исключения компонента inference_comp (ml_service)."""

from __future__ import annotations


class InferenceError(Exception):
    """Базовая ошибка инференса."""


class InvalidTimeSeriesError(InferenceError, ValueError):
    """Некорректный временной ряд (пустой, NaN, бесконечность)."""


class InvalidHorizonError(InferenceError, ValueError):
    """Некорректный горизонт прогноза."""


class InsufficientDataError(InferenceError):
    """В ряду слишком мало наблюдений для выбранной модели."""


class ModelNotAvailableError(InferenceError):
    """Библиотека модели (xgboost / statsmodels) не установлена."""


class ModelFitError(InferenceError):
    """Не удалось обучить или применить модель к данному ряду."""
