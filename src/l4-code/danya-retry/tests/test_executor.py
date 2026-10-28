"""Тесты RetryExecutor: повторы, лимит, dead-letter, смена стратегии."""

from __future__ import annotations

import pytest

from retry_comp import (
    ExponentialBackoffStrategy,
    FixedDelayStrategy,
    InMemoryDeadLetterQueue,
    PermanentError,
    RetryExecutor,
    RetryStatus,
)

from conftest import FakeSleep, FlakyTask


def test_success_on_first_attempt_no_waiting(fake_sleep: FakeSleep) -> None:
    executor = RetryExecutor(FixedDelayStrategy(2), sleep=fake_sleep)
    result = executor.execute(FlakyTask(0))
    assert result.succeeded and result.value == "ok"
    assert result.attempts == 1
    assert fake_sleep.calls == []


def test_fails_twice_then_succeeds_fixed(fake_sleep: FakeSleep) -> None:
    """Сценарий из ТЗ: два сбоя, успех на третьей попытке."""
    task = FlakyTask(2)
    executor = RetryExecutor(FixedDelayStrategy(2), max_attempts=3, sleep=fake_sleep)
    result = executor.execute(task)
    assert result.status is RetryStatus.SUCCESS
    assert result.attempts == 3 and task.calls == 3
    assert fake_sleep.calls == [2, 2]
    assert result.delays == (2, 2)
    assert len(result.errors) == 2


def test_fails_twice_then_succeeds_exponential(fake_sleep: FakeSleep) -> None:
    executor = RetryExecutor(ExponentialBackoffStrategy(2), max_attempts=3, sleep=fake_sleep)
    result = executor.execute(FlakyTask(2))
    assert result.succeeded
    assert fake_sleep.calls == [2, 4]


def test_attempts_exhausted_goes_to_dead_letter(fake_sleep: FakeSleep) -> None:
    dlq = InMemoryDeadLetterQueue()
    executor = RetryExecutor(
        FixedDelayStrategy(2), max_attempts=3, sleep=fake_sleep, dead_letter_sink=dlq
    )
    result = executor.execute(FlakyTask(10), task_name="retrain")
    assert result.status is RetryStatus.EXHAUSTED
    assert not result.succeeded and result.value is None
    assert result.attempts == 3
    assert fake_sleep.calls == [2, 2]  # после последней попытки не ждём
    assert len(dlq.items) == 1
    assert dlq.items[0].task_name == "retrain"
    assert dlq.items[0].attempts == 3


def test_permanent_error_is_not_retried(fake_sleep: FakeSleep) -> None:
    calls = 0

    def bad() -> str:
        nonlocal calls
        calls += 1
        raise PermanentError("неверный формат")

    dlq = InMemoryDeadLetterQueue()
    executor = RetryExecutor(
        FixedDelayStrategy(2), max_attempts=5, sleep=fake_sleep, dead_letter_sink=dlq
    )
    result = executor.execute(bad, task_name="bad")
    assert result.status is RetryStatus.PERMANENT_FAILURE
    assert calls == 1 and result.attempts == 1
    assert fake_sleep.calls == []
    assert len(dlq.items) == 1 and "неверный формат" in dlq.items[0].reason


def test_switch_strategy_at_runtime(fake_sleep: FakeSleep) -> None:
    executor = RetryExecutor(FixedDelayStrategy(2), max_attempts=3, sleep=fake_sleep)
    executor.execute(FlakyTask(2))
    assert fake_sleep.calls == [2, 2]

    executor.set_strategy(ExponentialBackoffStrategy(2))
    executor.execute(FlakyTask(2))
    assert fake_sleep.calls == [2, 2, 2, 4]


def test_works_without_dead_letter_sink(fake_sleep: FakeSleep) -> None:
    executor = RetryExecutor(FixedDelayStrategy(1), max_attempts=2, sleep=fake_sleep)
    result = executor.execute(FlakyTask(5))
    assert result.status is RetryStatus.EXHAUSTED


def test_single_attempt_means_no_retries(fake_sleep: FakeSleep) -> None:
    executor = RetryExecutor(FixedDelayStrategy(2), max_attempts=1, sleep=fake_sleep)
    result = executor.execute(FlakyTask(1))
    assert result.status is RetryStatus.EXHAUSTED
    assert fake_sleep.calls == []


@pytest.mark.parametrize("bad_attempts", [0, -3])
def test_invalid_max_attempts_rejected(bad_attempts: int) -> None:
    with pytest.raises(ValueError):
        RetryExecutor(FixedDelayStrategy(1), max_attempts=bad_attempts)


def test_executor_returns_typed_value(fake_sleep: FakeSleep) -> None:
    executor = RetryExecutor(FixedDelayStrategy(0), sleep=fake_sleep)
    result = executor.execute(lambda: 42)
    assert result.value == 42
