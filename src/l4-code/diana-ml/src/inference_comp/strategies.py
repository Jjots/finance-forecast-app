"""Стратегии прогнозирования (паттерн Strategy) для inference_comp.

Настоящие модели (xgboost, statsmodels) подключаются лениво: если библиотека
не установлена, при использовании по умолчанию бросается ModelNotAvailableError.
Фабрики моделей можно подменить (внедрение зависимостей) — так стратегии
проверяются в тестах без тяжёлых библиотек.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Protocol, Sequence

import numpy as np

from .errors import InsufficientDataError, ModelFitError, ModelNotAvailableError
from .features import FloatArray, make_lag_matrix
from .models import PredictionResult, TimeSeriesData, validate_horizon


class ForecastStrategy(ABC):
    """Единый контракт модели прогнозирования для любого клиента."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Короткое имя модели (попадает в PredictionResult)."""

    @abstractmethod
    def predict(self, data: TimeSeriesData, horizon: int) -> PredictionResult:
        """Построить прогноз на ``horizon`` периодов вперёд."""


# --------------------------------------------------------------------------
# XGBoost
# --------------------------------------------------------------------------

class RegressorLike(Protocol):
    """Минимальный интерфейс регрессора (совместим с xgboost.XGBRegressor)."""

    def fit(self, x: FloatArray, y: FloatArray) -> object:
        ...

    def predict(self, x: FloatArray) -> FloatArray:
        ...


RegressorFactory = Callable[[], RegressorLike]


def default_xgboost_factory() -> RegressorLike:
    """Создать настоящий XGBRegressor (импорт отложен до первого использования)."""
    try:
        from xgboost import XGBRegressor

        return XGBRegressor(  # type: ignore[no-any-return]
            n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42
        )
    except Exception as exc:  # ImportError, XGBoostError (нет libomp), нет scikit-learn
        raise ModelNotAvailableError(
            "xgboost недоступен (не установлен, нет scikit-learn или системной "
            f"библиотеки OpenMP; на macOS: brew install libomp): {exc}"
        ) from exc


class XGBoostStrategy(ForecastStrategy):
    """Градиентный бустинг на лагах ряда с рекурсивным многошаговым прогнозом.

    Прототип обучает модель на переданном ряду. В целевой системе обученная
    модель загружается из model_registry_comp, а признаки строит feature_engineer_comp.
    """

    def __init__(self, n_lags: int = 3, regressor_factory: RegressorFactory | None = None) -> None:
        if n_lags < 1:
            raise ValueError("n_lags должен быть >= 1")
        self._n_lags = n_lags
        self._factory: RegressorFactory = regressor_factory or default_xgboost_factory

    @property
    def name(self) -> str:
        return "xgboost"

    def predict(self, data: TimeSeriesData, horizon: int) -> PredictionResult:
        validate_horizon(horizon)
        x, y = make_lag_matrix(data.values, self._n_lags)  # InsufficientDataError
        model = self._factory()
        try:
            model.fit(x, y)
            window = list(data.values[-self._n_lags :])
            forecast: list[float] = []
            for _ in range(horizon):
                features = np.asarray([window[-self._n_lags :]], dtype=np.float64)
                next_value = float(model.predict(features)[0])
                forecast.append(next_value)
                window.append(next_value)  # рекурсивный шаг: прогноз становится лагом
        except (ValueError, np.linalg.LinAlgError) as exc:
            raise ModelFitError(f"XGBoost не смог построить прогноз: {exc}") from exc
        return PredictionResult(horizon=horizon, values=tuple(forecast), model_name=self.name)


# --------------------------------------------------------------------------
# ARIMA
# --------------------------------------------------------------------------

class ArimaFitted(Protocol):
    """Результат обучения (совместим с результатом statsmodels ARIMA.fit())."""

    def forecast(self, steps: int) -> Sequence[float]:
        ...


class ArimaModel(Protocol):
    """Необученная модель (совместим с statsmodels.tsa.arima.model.ARIMA)."""

    def fit(self) -> ArimaFitted:
        ...


ArimaOrder = tuple[int, int, int]
ArimaFactory = Callable[[Sequence[float], ArimaOrder], ArimaModel]


def default_arima_factory(values: Sequence[float], order: ArimaOrder) -> ArimaModel:
    """Создать настоящую модель statsmodels ARIMA (импорт отложен)."""
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError as exc:
        raise ModelNotAvailableError(
            "библиотека statsmodels не установлена: pip install statsmodels"
        ) from exc
    return ARIMA(np.asarray(values, dtype=np.float64), order=order)  # type: ignore[no-any-return]


class ARIMAStrategy(ForecastStrategy):
    """Классическая модель ARIMA(p, d, q): ряд подаётся как есть, без лагов."""

    def __init__(
        self,
        order: ArimaOrder = (1, 1, 1),
        min_observations: int = 8,
        model_factory: ArimaFactory | None = None,
    ) -> None:
        if len(order) != 3 or any(not isinstance(v, int) or v < 0 for v in order):
            raise ValueError("order должен быть кортежем из трёх неотрицательных int (p, d, q)")
        if min_observations < 1:
            raise ValueError("min_observations должен быть >= 1")
        self._order = order
        self._min_observations = min_observations
        self._factory: ArimaFactory = model_factory or default_arima_factory

    @property
    def name(self) -> str:
        return "arima"

    def predict(self, data: TimeSeriesData, horizon: int) -> PredictionResult:
        validate_horizon(horizon)
        if len(data) < self._min_observations:
            raise InsufficientDataError(
                f"для ARIMA{self._order} нужно минимум {self._min_observations} "
                f"наблюдений, получено {len(data)}"
            )
        try:
            fitted = self._factory(data.values, self._order).fit()
            raw = fitted.forecast(steps=horizon)
            values = tuple(float(v) for v in raw)
        except (ValueError, np.linalg.LinAlgError) as exc:
            raise ModelFitError(f"ARIMA не смогла построить прогноз: {exc}") from exc
        return PredictionResult(horizon=horizon, values=values, model_name=self.name)
