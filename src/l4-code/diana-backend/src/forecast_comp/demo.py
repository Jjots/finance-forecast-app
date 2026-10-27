"""Демонстрация forecast_comp: переключение стратегий на лету.

Запуск:  PYTHONPATH=src python -m forecast_comp.demo
Кэш и ML-клиент — имитаторы (см. fakes.py).
"""

from __future__ import annotations

from .errors import CacheMissError, ForecastError
from .fakes import FakeMlClient, InMemoryForecastCache
from .models import ForecastRequest, ForecastResult
from .service import ForecastService
from .strategies import (
    CachedForecastStrategy,
    FallbackForecastStrategy,
    MlForecastStrategy,
)


def _show(title: str, result: ForecastResult) -> None:
    print(f"{title}: source={result.source.value}, "
          f"calculated_at={result.calculated_at:%Y-%m-%d %H:%M}, "
          f"values[:3]={list(result.values[:3])}")


def main() -> None:
    cache = InMemoryForecastCache()
    ml_client = FakeMlClient()
    request = ForecastRequest(company_id=100, horizon=12)

    # 1. Кэш пуст -> стратегия кэша сообщает об отсутствии прогноза.
    service = ForecastService(CachedForecastStrategy(cache))
    try:
        service.get_forecast(request)
    except CacheMissError as exc:
        print(f"1) Кэш пуст: {exc}")

    # 2. Переключаемся на ML: считаем новый прогноз и кладём его в кэш.
    service.set_strategy(MlForecastStrategy(ml_client, writer=cache))
    _show("2) ML-расчёт", service.get_forecast(request))

    # 3. Возвращаемся к кэшу: теперь результат есть, ML не вызывается.
    calls_before = ml_client.calls
    service.set_strategy(CachedForecastStrategy(cache))
    _show("3) Из кэша ", service.get_forecast(request))
    assert ml_client.calls == calls_before, "ML не должен вызываться при чтении из кэша"

    # 4. Политика «ML, при недоступности — кэш».
    ml_client.available = False
    service.set_strategy(
        FallbackForecastStrategy(MlForecastStrategy(ml_client), CachedForecastStrategy(cache))
    )
    _show("4) ML недоступен -> fallback", service.get_forecast(request))

    # 5. Некорректный запрос.
    try:
        ForecastRequest(company_id=100, horizon=0)
    except ForecastError as exc:
        print(f"5) Некорректный запрос: {exc}")


if __name__ == "__main__":
    main()
