"""ИМИТАЦИИ моделей для запуска без xgboost / statsmodels.

ВНИМАНИЕ: это НЕ обученные XGBoost и ARIMA. Это простые заглушки с тем же
программным интерфейсом, нужные, чтобы показать паттерн Strategy и
прогнать тесты логики без тяжёлых зависимостей. Их числа не отражают
качество реальных моделей.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .features import FloatArray
from .strategies import ArimaFitted, ArimaModel, ArimaOrder


class LeastSquaresRegressor:
    """Имитация XGBRegressor: линейная регрессия по лагам (метод наименьших квадратов)."""

    def __init__(self) -> None:
        self._coef: FloatArray | None = None

    def fit(self, x: FloatArray, y: FloatArray) -> "LeastSquaresRegressor":
        design = np.hstack([x, np.ones((x.shape[0], 1))])
        self._coef, *_ = np.linalg.lstsq(design, y, rcond=None)
        return self

    def predict(self, x: FloatArray) -> FloatArray:
        if self._coef is None:
            raise ValueError("модель не обучена")
        design = np.hstack([x, np.ones((x.shape[0], 1))])
        return design @ self._coef  # type: ignore[no-any-return]


class _DriftFitted:
    def __init__(self, last: float, drift: float) -> None:
        self._last = last
        self._drift = drift

    def forecast(self, steps: int) -> Sequence[float]:
        return [self._last + self._drift * k for k in range(1, steps + 1)]


class DriftArimaModel:
    """Имитация ARIMA: случайное блуждание со сносом (последнее значение + средний прирост)."""

    def __init__(self, values: Sequence[float]) -> None:
        self._values = list(values)

    def fit(self) -> ArimaFitted:
        diffs = np.diff(np.asarray(self._values, dtype=np.float64))
        drift = float(diffs.mean()) if diffs.size else 0.0
        return _DriftFitted(self._values[-1], drift)


def drift_arima_factory(values: Sequence[float], order: ArimaOrder) -> ArimaModel:
    """Фабрика-имитация, совместимая с ARIMAStrategy(model_factory=...)."""
    return DriftArimaModel(values)
