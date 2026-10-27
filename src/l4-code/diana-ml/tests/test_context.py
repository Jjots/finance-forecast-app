from __future__ import annotations

import pytest

from inference_comp import (
    ARIMAStrategy,
    ForecastContext,
    ForecastStrategy,
    InvalidHorizonError,
    PredictionResult,
    TimeSeriesData,
    XGBoostStrategy,
)
from inference_comp.stubs import LeastSquaresRegressor, drift_arima_factory

DATA = TimeSeriesData.from_sequence([100, 108, 115, 125, 131, 142, 150, 161, 170, 182])


def make_strategies() -> tuple[ForecastStrategy, ForecastStrategy]:
    return (
        XGBoostStrategy(n_lags=3, regressor_factory=LeastSquaresRegressor),
        ARIMAStrategy(model_factory=drift_arima_factory),
    )


def test_same_api_for_both_models_and_switching() -> None:
    """Сценарий из ТЗ: predict -> set_strategy -> predict, одинаковый интерфейс."""
    xgb, arima = make_strategies()
    context = ForecastContext(xgb)

    first = context.predict(DATA, horizon=3)
    assert context.strategy_name == "xgboost"

    context.set_strategy(arima)
    second = context.predict(DATA, horizon=3)
    assert context.strategy_name == "arima"

    for result in (first, second):
        assert isinstance(result, PredictionResult)
        assert result.horizon == 3 and len(result.values) == 3
    assert (first.model_name, second.model_name) == ("xgboost", "arima")


def test_strategy_can_be_switched_back_and_forth() -> None:
    xgb, arima = make_strategies()
    context = ForecastContext(xgb)
    names = []
    for strategy in (arima, xgb, arima):
        context.set_strategy(strategy)
        names.append(context.predict(DATA, horizon=1).model_name)
    assert names == ["arima", "xgboost", "arima"]


@pytest.mark.parametrize("horizon", [0, -2])
def test_context_rejects_invalid_horizon(horizon: int) -> None:
    xgb, _ = make_strategies()
    with pytest.raises(InvalidHorizonError):
        ForecastContext(xgb).predict(DATA, horizon=horizon)


def test_constructor_rejects_non_strategy() -> None:
    with pytest.raises(TypeError):
        ForecastContext(object())  # type: ignore[arg-type]


def test_set_strategy_rejects_non_strategy() -> None:
    xgb, _ = make_strategies()
    context = ForecastContext(xgb)
    with pytest.raises(TypeError):
        context.set_strategy("arima")  # type: ignore[arg-type]
    assert context.strategy_name == "xgboost"  # прежняя стратегия сохранилась
