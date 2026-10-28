from __future__ import annotations

from datetime import datetime, timezone

import pytest

from forecast_comp import (
    CacheMissError,
    CachedForecastStrategy,
    ForecastRequest,
    ForecastResult,
    ForecastService,
    ForecastSource,
    MlForecastStrategy,
)
from forecast_comp.fakes import FakeMlClient, InMemoryForecastCache

REQUEST = ForecastRequest(company_id=100, horizon=12)


def test_switching_strategy_at_runtime() -> None:
    """Сценарий из ТЗ: кэш -> set_strategy(ML) -> другой источник результата."""
    cache = InMemoryForecastCache()
    cache.put(
        ForecastResult(
            100, 12, tuple(float(i) for i in range(12)), ForecastSource.ML,
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    )
    ml_client = FakeMlClient()
    service = ForecastService(CachedForecastStrategy(cache))

    first = service.get_forecast(REQUEST)
    assert first.source is ForecastSource.CACHE
    assert ml_client.calls == 0

    service.set_strategy(MlForecastStrategy(ml_client))
    second = service.get_forecast(REQUEST)
    assert second.source is ForecastSource.ML
    assert ml_client.calls == 1
    assert first.values != second.values


def test_service_propagates_strategy_errors() -> None:
    service = ForecastService(CachedForecastStrategy(InMemoryForecastCache()))
    with pytest.raises(CacheMissError):
        service.get_forecast(REQUEST)


def test_constructor_rejects_non_strategy() -> None:
    with pytest.raises(TypeError):
        ForecastService(object())  # type: ignore[arg-type]


def test_set_strategy_rejects_non_strategy() -> None:
    service = ForecastService(CachedForecastStrategy(InMemoryForecastCache()))
    with pytest.raises(TypeError):
        service.set_strategy("ml")  # type: ignore[arg-type]
