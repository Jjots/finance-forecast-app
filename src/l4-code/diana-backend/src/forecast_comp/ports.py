"""Порты (зависимости) forecast_comp.

Соответствуют инфраструктурным компонентам backend из L3:
* ForecastCacheReader / ForecastCacheWriter — db_repo_comp (кэш и история прогнозов);
* MlClient — ml_client_comp (вызовы ml_service).

Интерфейсы узкие (принцип ISP): стратегии зависят только от того, что используют.
"""

from __future__ import annotations

from typing import Optional, Protocol, Sequence

from .models import ForecastResult


class ForecastCacheReader(Protocol):
    """Чтение сохранённого прогноза."""

    def get(self, company_id: int, horizon: int) -> Optional[ForecastResult]:
        """Вернуть сохранённый прогноз или None, если его нет."""
        ...


class ForecastCacheWriter(Protocol):
    """Сохранение рассчитанного прогноза."""

    def put(self, result: ForecastResult) -> None:
        """Сохранить результат (перезаписывает прежний для той же пары)."""
        ...


class MlClient(Protocol):
    """Клиент ML-сервиса.

    Контракт: возвращает ``horizon`` чисел; при недоступности сервиса
    бросает MlServiceUnavailableError.
    """

    def predict(self, company_id: int, horizon: int) -> Sequence[float]:
        ...
