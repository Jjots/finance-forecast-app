"""Тесты стратегий расчёта паузы."""

from __future__ import annotations

import pytest

from retry_comp import ExponentialBackoffStrategy, FixedDelayStrategy, RetryStrategy


def test_fixed_delay_is_constant() -> None:
    strategy = FixedDelayStrategy(delay=2)
    assert [strategy.execute(n) for n in (1, 2, 3)] == [2, 2, 2]


def test_exponential_backoff_doubles() -> None:
    strategy = ExponentialBackoffStrategy(base_delay=2)
    assert [strategy.execute(n) for n in (1, 2, 3)] == [2, 4, 8]


def test_exponential_backoff_respects_max_delay() -> None:
    strategy = ExponentialBackoffStrategy(base_delay=2, max_delay=5)
    assert [strategy.execute(n) for n in (1, 2, 3, 4)] == [2, 4, 5, 5]


def test_exponential_backoff_custom_factor() -> None:
    strategy = ExponentialBackoffStrategy(base_delay=1, factor=3)
    assert [strategy.execute(n) for n in (1, 2, 3)] == [1, 3, 9]


@pytest.mark.parametrize("strategy", [FixedDelayStrategy(1), ExponentialBackoffStrategy(1)])
def test_both_strategies_share_contract(strategy: RetryStrategy) -> None:
    """LSP: любая стратегия возвращает неотрицательное число."""
    assert isinstance(strategy, RetryStrategy)
    assert strategy.execute(1) >= 0


@pytest.mark.parametrize("strategy", [FixedDelayStrategy(1), ExponentialBackoffStrategy(1)])
@pytest.mark.parametrize("bad_number", [0, -1])
def test_retry_number_must_be_positive(strategy: RetryStrategy, bad_number: int) -> None:
    with pytest.raises(ValueError):
        strategy.execute(bad_number)


def test_negative_fixed_delay_rejected() -> None:
    with pytest.raises(ValueError):
        FixedDelayStrategy(delay=-1)


@pytest.mark.parametrize(
    "kwargs",
    [{"base_delay": -1}, {"factor": 0.5}, {"max_delay": -1}],
)
def test_invalid_exponential_parameters_rejected(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        ExponentialBackoffStrategy(**kwargs)


def test_strategy_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        RetryStrategy()  # type: ignore[abstract]
