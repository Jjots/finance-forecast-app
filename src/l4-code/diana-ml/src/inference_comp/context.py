"""Контекст паттерна Strategy: ForecastContext (inference_comp)."""

from __future__ import annotations

from .models import PredictionResult, TimeSeriesData, validate_horizon
from .strategies import ForecastStrategy


class ForecastContext:
    """Единая точка входа инференса; модель подменяется во время выполнения."""

    def __init__(self, strategy: ForecastStrategy) -> None:
        self._strategy = self._checked(strategy)

    @staticmethod
    def _checked(strategy: ForecastStrategy) -> ForecastStrategy:
        if not isinstance(strategy, ForecastStrategy):
            raise TypeError(
                "strategy должна быть экземпляром ForecastStrategy, "
                f"получено {type(strategy).__name__}"
            )
        return strategy

    def set_strategy(self, strategy: ForecastStrategy) -> None:
        """Заменить модель прогнозирования."""
        self._strategy = self._checked(strategy)

    @property
    def strategy_name(self) -> str:
        """Имя текущей модели."""
        return self._strategy.name

    def predict(self, data: TimeSeriesData, horizon: int) -> PredictionResult:
        """Построить прогноз текущей моделью (одинаковый API для любой стратегии)."""
        validate_horizon(horizon)
        return self._strategy.predict(data, horizon)
