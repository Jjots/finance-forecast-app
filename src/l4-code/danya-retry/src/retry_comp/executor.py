"""RetryExecutor - контекст паттерна Strategy для компонента retry_comp."""

from __future__ import annotations

import time
from typing import Callable, Optional, TypeVar

from .dead_letter import DeadLetterSink
from .errors import PermanentError
from .models import DeadLetter, RetryResult, RetryStatus
from .strategies import RetryStrategy

T = TypeVar("T")

Sleeper = Callable[[float], None]
"""Функция ожидания; в тестах подменяется, чтобы не ждать по-настоящему."""


class RetryExecutor:
    """Выполняет задачу с повторами; алгоритм паузы берёт из текущей стратегии.

    Ответственность класса - только порядок попыток. Расчёт паузы делает
    стратегия, ожидание - внедряемая функция ``sleep``, хранение неудачных
    задач - внедряемый ``dead_letter_sink``.
    """

    def __init__(
        self,
        strategy: RetryStrategy,
        max_attempts: int = 3,
        sleep: Sleeper = time.sleep,
        dead_letter_sink: Optional[DeadLetterSink] = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts должен быть >= 1")
        self._strategy = strategy
        self._max_attempts = max_attempts
        self._sleep = sleep
        self._dead_letter_sink = dead_letter_sink

    def set_strategy(self, strategy: RetryStrategy) -> None:
        """Сменить алгоритм паузы во время работы."""
        self._strategy = strategy

    def execute(self, task: Callable[[], T], task_name: str = "task") -> RetryResult[T]:
        """Выполнить ``task``; при ошибке повторять не более ``max_attempts`` раз."""
        errors: list[str] = []
        delays: list[float] = []

        for attempt in range(1, self._max_attempts + 1):
            try:
                value = task()
            except PermanentError as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
                return self._fail(
                    RetryStatus.PERMANENT_FAILURE, task_name, attempt, delays, errors
                )
            except Exception as exc:  # любая другая ошибка - повторяем
                errors.append(f"{type(exc).__name__}: {exc}")
                if attempt == self._max_attempts:
                    break
                delay = self._strategy.execute(attempt)
                delays.append(delay)
                self._sleep(delay)
            else:
                return RetryResult(
                    RetryStatus.SUCCESS, value, attempt, tuple(delays), tuple(errors)
                )

        return self._fail(
            RetryStatus.EXHAUSTED, task_name, self._max_attempts, delays, errors
        )

    def _fail(
        self,
        status: RetryStatus,
        task_name: str,
        attempts: int,
        delays: list[float],
        errors: list[str],
    ) -> RetryResult[T]:
        if self._dead_letter_sink is not None:
            self._dead_letter_sink.publish(
                DeadLetter(task_name=task_name, reason=errors[-1], attempts=attempts)
            )
        return RetryResult(status, None, attempts, tuple(delays), tuple(errors))
