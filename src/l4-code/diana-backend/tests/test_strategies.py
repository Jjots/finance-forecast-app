from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

import pytest

from forecast_comp import (
    CacheMissError,
    CachedForecastStrategy,
    FallbackForecastStrategy,
    ForecastRequest,
    ForecastResult,
    ForecastRetrievalStrategy,
    ForecastSource,
    InvalidMlResponseError,
    MlForecastStrategy,
    MlServiceUnavailableError,
)
from forecast_comp.fakes import FakeMlClient, InMemoryForecastCache

FIXED_TIME = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
REQUEST = ForecastRequest(company_id=100, horizon=3)


def fixed_clock() -> datetime:
    return FIXED_TIME


class BadLengthClient:
    def predict(self, company_id: int, horizon: int) -> Sequence[float]:
        return [1.0]  # меньше, чем horizon


class NanClient:
    def predict(self, company_id: int, horizon: int) -> Sequence[float]:
        return [1.0, float("nan"), 3.0]


# --- CachedForecastStrategy -------------------------------------------------

def test_cached_returns_stored_with_cache_source() -> None:
    cache = InMemoryForecastCache()
    stored_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    cache.put(ForecastResult(100, 3, (1.0, 2.0, 3.0), ForecastSource.ML, stored_at))

    result = CachedForecastStrategy(cache).execute(REQUEST)

    assert result.source is ForecastSource.CACHE
    assert result.values == (1.0, 2.0, 3.0)
    assert result.calculated_at == stored_at  # время исходного расчёта сохраняется


def test_cached_miss_raises() -> None:
    with pytest.raises(CacheMissError):
        CachedForecastStrategy(InMemoryForecastCache()).execute(REQUEST)


def test_cached_does_not_mutate_stored_entry() -> None:
    cache = InMemoryForecastCache()
    original = ForecastResult(100, 3, (1.0, 2.0, 3.0), ForecastSource.ML, FIXED_TIME)
    cache.put(original)
    CachedForecastStrategy(cache).execute(REQUEST)
    assert cache.get(100, 3) is original
    assert original.source is ForecastSource.ML


# --- MlForecastStrategy -----------------------------------------------------

def test_ml_returns_fresh_result() -> None:
    client = FakeMlClient(base=100.0, step=10.0)
    result = MlForecastStrategy(client, clock=fixed_clock).execute(REQUEST)

    assert result.source is ForecastSource.ML
    assert result.values == (110.0, 120.0, 130.0)
    assert result.calculated_at == FIXED_TIME
    assert client.calls == 1


def test_ml_writes_result_to_cache_when_writer_given() -> None:
    cache = InMemoryForecastCache()
    MlForecastStrategy(FakeMlClient(), writer=cache, clock=fixed_clock).execute(REQUEST)
    stored = cache.get(100, 3)
    assert stored is not None and stored.source is ForecastSource.ML


def test_ml_unavailable_propagates() -> None:
    client = FakeMlClient(available=False)
    with pytest.raises(MlServiceUnavailableError):
        MlForecastStrategy(client).execute(REQUEST)


def test_ml_wrong_length_is_rejected() -> None:
    with pytest.raises(InvalidMlResponseError):
        MlForecastStrategy(BadLengthClient()).execute(REQUEST)


def test_ml_nan_is_rejected() -> None:
    with pytest.raises(InvalidMlResponseError):
        MlForecastStrategy(NanClient()).execute(REQUEST)


# --- FallbackForecastStrategy ----------------------------------------------

def _fallback(client: object, cache: InMemoryForecastCache) -> FallbackForecastStrategy:
    return FallbackForecastStrategy(
        MlForecastStrategy(client, clock=fixed_clock),  # type: ignore[arg-type]
        CachedForecastStrategy(cache),
    )


def test_fallback_uses_ml_when_available() -> None:
    cache = InMemoryForecastCache()
    result = _fallback(FakeMlClient(), cache).execute(REQUEST)
    assert result.source is ForecastSource.ML


def test_fallback_uses_cache_when_ml_down() -> None:
    cache = InMemoryForecastCache()
    cache.put(ForecastResult(100, 3, (7.0, 8.0, 9.0), ForecastSource.ML, FIXED_TIME))
    result = _fallback(FakeMlClient(available=False), cache).execute(REQUEST)
    assert result.source is ForecastSource.CACHE
    assert result.values == (7.0, 8.0, 9.0)


def test_fallback_fails_when_both_unavailable() -> None:
    with pytest.raises(CacheMissError):
        _fallback(FakeMlClient(available=False), InMemoryForecastCache()).execute(REQUEST)


def test_fallback_does_not_mask_invalid_ml_response() -> None:
    cache = InMemoryForecastCache()
    cache.put(ForecastResult(100, 3, (7.0, 8.0, 9.0), ForecastSource.ML, FIXED_TIME))
    with pytest.raises(InvalidMlResponseError):
        _fallback(BadLengthClient(), cache).execute(REQUEST)


# --- Общий контракт ---------------------------------------------------------

def test_all_strategies_share_one_contract() -> None:
    cache = InMemoryForecastCache()
    strategies: list[ForecastRetrievalStrategy] = [
        CachedForecastStrategy(cache),
        MlForecastStrategy(FakeMlClient()),
        FallbackForecastStrategy(MlForecastStrategy(FakeMlClient()), CachedForecastStrategy(cache)),
    ]
    for strategy in strategies:
        assert isinstance(strategy, ForecastRetrievalStrategy)
