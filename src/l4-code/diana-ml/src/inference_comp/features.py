"""Подготовка признаков для XGBoost (роль feature_engineer_comp из L3).

Для ARIMA признаки не нужны: модель принимает сам ряд.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from .errors import InsufficientDataError

FloatArray = NDArray[np.float64]


def make_lag_matrix(values: Sequence[float], n_lags: int) -> tuple[FloatArray, FloatArray]:
    """Построить обучающую выборку на лагах.

    Строка ``i`` матрицы X — это ``values[i : i + n_lags]``, цель ``y[i]`` —
    ``values[i + n_lags]``. Для ряда длины N получается N - n_lags строк.
    """
    if n_lags < 1:
        raise ValueError("n_lags должен быть >= 1")
    if len(values) <= n_lags:
        raise InsufficientDataError(
            f"для n_lags={n_lags} нужно минимум {n_lags + 1} наблюдений, получено {len(values)}"
        )
    series = np.asarray(values, dtype=np.float64)
    rows = len(series) - n_lags
    x = np.stack([series[i : i + n_lags] for i in range(rows)])
    y = series[n_lags:]
    return x, y
