"""Контекст паттерна Strategy: ForecastService (forecast_comp)."""

from __future__ import annotations

from .models import ForecastRequest, ForecastResult
from .strategies import ForecastRetrievalStrategy


class ForecastService:
    """Выдаёт прогноз, делегируя получение текущей стратегии.

    Вызывающий код (роутер FastAPI) не знает, откуда пришёл результат;
    стратегию можно менять во время выполнения.
    """

    def __init__(self, strategy: ForecastRetrievalStrategy) -> None:
        self._strategy = self._checked(strategy)

    @staticmethod
    def _checked(strategy: ForecastRetrievalStrategy) -> ForecastRetrievalStrategy:
        if not isinstance(strategy, ForecastRetrievalStrategy):
            raise TypeError(
                "strategy должна быть экземпляром ForecastRetrievalStrategy, "
                f"получено {type(strategy).__name__}"
            )
        return strategy

    def set_strategy(self, strategy: ForecastRetrievalStrategy) -> None:
        """Заменить стратегию получения прогноза."""
        self._strategy = self._checked(strategy)

    def get_forecast(self, request: ForecastRequest) -> ForecastResult:
        """Получить прогноз текущей стратегией."""
        return self._strategy.execute(request)
