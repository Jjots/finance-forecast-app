"""Тесты на НАСТОЯЩИХ xgboost и statsmodels.

Если библиотеки не установлены, тесты пропускаются (pytest.importorskip).
Для полной проверки:  pip install -r requirements.txt
"""

from __future__ import annotations

import math

import pytest

from inference_comp import ARIMAStrategy, ForecastContext, TimeSeriesData, XGBoostStrategy

DATA = TimeSeriesData.from_sequence([100, 108, 115, 125, 131, 142, 150, 161, 170, 182])


def test_real_xgboost_forecast() -> None:
    pytest.importorskip("xgboost")
    result = XGBoostStrategy(n_lags=3).predict(DATA, horizon=3)
    assert result.model_name == "xgboost"
    assert len(result.values) == 3 and all(math.isfinite(v) for v in result.values)


def test_real_arima_forecast() -> None:
    pytest.importorskip("statsmodels")
    result = ARIMAStrategy(order=(1, 1, 1)).predict(DATA, horizon=3)
    assert result.model_name == "arima"
    assert len(result.values) == 3 and all(math.isfinite(v) for v in result.values)
    # ряд растёт, ARIMA с d=1 должна продолжить рост выше последнего наблюдения
    assert result.values[-1] > DATA.values[-1]


def test_real_models_share_one_api_via_context() -> None:
    pytest.importorskip("xgboost")
    pytest.importorskip("statsmodels")
    context = ForecastContext(XGBoostStrategy(n_lags=3))
    first = context.predict(DATA, horizon=3)
    context.set_strategy(ARIMAStrategy())
    second = context.predict(DATA, horizon=3)
    assert (first.model_name, second.model_name) == ("xgboost", "arima")
    assert first.horizon == second.horizon == 3
