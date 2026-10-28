"""Тесты логики стратегий на имитациях моделей (без xgboost / statsmodels)."""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pytest

from inference_comp import (
    ARIMAStrategy,
    InsufficientDataError,
    ModelFitError,
    ModelNotAvailableError,
    TimeSeriesData,
    XGBoostStrategy,
)
from inference_comp.features import FloatArray
from inference_comp.stubs import LeastSquaresRegressor, drift_arima_factory

LINEAR = TimeSeriesData.from_sequence([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])


# --- XGBoostStrategy (логика на имитации регрессора) -------------------------

def test_xgboost_recursive_forecast_follows_linear_trend() -> None:
    strategy = XGBoostStrategy(n_lags=2, regressor_factory=LeastSquaresRegressor)
    result = strategy.predict(LINEAR, horizon=3)
    assert result.model_name == "xgboost"
    assert result.horizon == 3
    assert result.values == pytest.approx((110.0, 120.0, 130.0), abs=1e-6)


def test_xgboost_creates_model_and_trains_on_lag_matrix() -> None:
    seen: dict[str, tuple[int, ...]] = {}

    class Spy:
        def fit(self, x: FloatArray, y: FloatArray) -> object:
            seen["x"], seen["y"] = x.shape, y.shape
            return self

        def predict(self, x: FloatArray) -> FloatArray:
            return np.array([float(x[0, -1])])

    XGBoostStrategy(n_lags=3, regressor_factory=Spy).predict(LINEAR, horizon=2)
    assert seen["x"] == (7, 3) and seen["y"] == (7,)


def test_xgboost_series_too_short() -> None:
    strategy = XGBoostStrategy(n_lags=3, regressor_factory=LeastSquaresRegressor)
    with pytest.raises(InsufficientDataError):
        strategy.predict(TimeSeriesData.from_sequence([1, 2, 3]), horizon=1)


def test_xgboost_fit_failure_is_wrapped() -> None:
    class Broken:
        def fit(self, x: FloatArray, y: FloatArray) -> object:
            raise ValueError("boom")

        def predict(self, x: FloatArray) -> FloatArray:
            raise AssertionError("не должно вызываться")

    with pytest.raises(ModelFitError):
        XGBoostStrategy(n_lags=2, regressor_factory=Broken).predict(LINEAR, horizon=1)


def test_xgboost_missing_library_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "xgboost":
            raise ImportError("no xgboost")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ModelNotAvailableError):
        XGBoostStrategy(n_lags=2).predict(LINEAR, horizon=1)


def test_xgboost_rejects_bad_n_lags() -> None:
    with pytest.raises(ValueError):
        XGBoostStrategy(n_lags=0)


# --- ARIMAStrategy (логика на имитации модели) -------------------------------

def test_arima_uses_factory_with_order_and_returns_forecast() -> None:
    calls: list[tuple[tuple[float, ...], tuple[int, int, int]]] = []

    class Fitted:
        def forecast(self, steps: int) -> Sequence[float]:
            return [float(i) for i in range(1, steps + 1)]

    class Model:
        def fit(self) -> Fitted:
            return Fitted()

    def factory(values: Sequence[float], order: tuple[int, int, int]) -> Model:
        calls.append((tuple(values), order))
        return Model()

    result = ARIMAStrategy(order=(2, 1, 0), model_factory=factory).predict(LINEAR, horizon=4)
    assert result.model_name == "arima"
    assert result.values == (1.0, 2.0, 3.0, 4.0)
    assert calls == [(LINEAR.values, (2, 1, 0))]


def test_arima_drift_stub_extends_trend() -> None:
    result = ARIMAStrategy(model_factory=drift_arima_factory).predict(LINEAR, horizon=2)
    assert result.values == pytest.approx((110.0, 120.0))


def test_arima_series_too_short() -> None:
    strategy = ARIMAStrategy(min_observations=8, model_factory=drift_arima_factory)
    with pytest.raises(InsufficientDataError):
        strategy.predict(TimeSeriesData.from_sequence([1, 2, 3]), horizon=2)


def test_arima_fit_failure_is_wrapped() -> None:
    class Model:
        def fit(self) -> object:
            raise np.linalg.LinAlgError("singular")

    with pytest.raises(ModelFitError):
        ARIMAStrategy(model_factory=lambda v, o: Model()).predict(LINEAR, horizon=1)  # type: ignore[arg-type,return-value]


@pytest.mark.parametrize("order", [(1, 1), (1, -1, 1), (1.0, 1, 1)])
def test_arima_rejects_bad_order(order: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        ARIMAStrategy(order=order)  # type: ignore[arg-type]
