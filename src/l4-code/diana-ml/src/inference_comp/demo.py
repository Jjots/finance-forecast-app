"""Демонстрация inference_comp: один API — две модели.

Запуск с настоящими моделями:   PYTHONPATH=src python -m inference_comp.demo
Запуск с ИМИТАЦИЯМИ моделей:    PYTHONPATH=src python -m inference_comp.demo --stub
(--stub не требует xgboost/statsmodels; результаты — заглушки, не обученные модели)
"""

from __future__ import annotations

import sys

from .context import ForecastContext
from .errors import InferenceError, ModelNotAvailableError
from .models import TimeSeriesData
from .strategies import ARIMAStrategy, ForecastStrategy, XGBoostStrategy

# Условный годовой ряд выручки (млрд руб.) — тестовые данные, не реальная отчётность.
REVENUE = TimeSeriesData.from_sequence(
    [100.0, 108.0, 115.0, 125.0, 131.0, 142.0, 150.0, 161.0, 170.0, 182.0]
)


def build_strategies(stub: bool) -> tuple[ForecastStrategy, ForecastStrategy]:
    if stub:
        from .stubs import LeastSquaresRegressor, drift_arima_factory

        return (
            XGBoostStrategy(n_lags=3, regressor_factory=LeastSquaresRegressor),
            ARIMAStrategy(order=(1, 1, 1), model_factory=drift_arima_factory),
        )
    return XGBoostStrategy(n_lags=3), ARIMAStrategy(order=(1, 1, 1))


def main(argv: list[str]) -> int:
    stub = "--stub" in argv
    label = "ИМИТАЦИЯ (stub)" if stub else "реальные модели"
    print(f"Режим: {label}")

    xgb, arima = build_strategies(stub)
    context = ForecastContext(xgb)
    try:
        first = context.predict(REVENUE, horizon=3)
        print(f"1) {first.model_name:8s} -> {[round(v, 1) for v in first.values]}")

        context.set_strategy(arima)
        second = context.predict(REVENUE, horizon=3)
        print(f"2) {second.model_name:8s} -> {[round(v, 1) for v in second.values]}")
    except ModelNotAvailableError as exc:
        print(f"Ошибка: {exc}\nУстановите зависимости (requirements.txt) или запустите с --stub")
        return 1

    try:
        context.predict(TimeSeriesData.from_sequence([1.0, 2.0]), horizon=3)
    except InferenceError as exc:
        print(f"3) Короткий ряд: {type(exc).__name__}: {exc}")

    try:
        context.predict(REVENUE, horizon=0)
    except InferenceError as exc:
        print(f"4) Неверный горизонт: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
