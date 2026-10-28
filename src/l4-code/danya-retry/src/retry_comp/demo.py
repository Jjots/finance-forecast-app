"""Демонстрация: задача падает дважды и проходит с третьей попытки.

Запуск:  python -m retry_comp.demo          (паузы имитируются, мгновенно)
         python -m retry_comp.demo --real   (настоящие паузы time.sleep)
"""

from __future__ import annotations

import sys
import time
from typing import Callable

from .dead_letter import InMemoryDeadLetterQueue
from .errors import PermanentError
from .executor import RetryExecutor
from .models import RetryResult
from .strategies import ExponentialBackoffStrategy, FixedDelayStrategy


class FlakyTask:
    """Тестовая задача: первые ``failures`` вызовов падают, дальше успех."""

    def __init__(self, failures: int) -> None:
        self._failures = failures
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        if self.calls <= self._failures:
            raise ConnectionError(f"ML-сервис недоступен (вызов {self.calls})")
        return "модель переобучена"


def _print_result(result: RetryResult[str]) -> None:
    print(f"статус: {result.status.value}, попыток: {result.attempts}")
    print(f"паузы: {list(result.delays)} c")
    for error in result.errors:
        print(f"  ошибка: {error}")
    if result.succeeded:
        print(f"результат: {result.value}")


def main(argv: list[str]) -> int:
    real = "--real" in argv

    def simulated_sleep(seconds: float) -> None:
        print(f"  ... пауза {seconds} c" + ("" if real else " (имитация)"))
        if real:
            time.sleep(seconds)

    sleep: Callable[[float], None] = simulated_sleep
    dlq = InMemoryDeadLetterQueue()

    executor = RetryExecutor(
        FixedDelayStrategy(delay=2), max_attempts=3, sleep=sleep, dead_letter_sink=dlq
    )
    print("\n--- FixedDelayStrategy (2 c): два сбоя, успех на 3-й попытке ---")
    _print_result(executor.execute(FlakyTask(2), "retrain"))

    executor.set_strategy(ExponentialBackoffStrategy(base_delay=2))
    print("\n--- ExponentialBackoffStrategy (2, 4, 8 c): стратегия сменена на лету ---")
    _print_result(executor.execute(FlakyTask(2), "retrain"))

    print("\n--- Лимит попыток исчерпан (задача падает всегда) ---")
    _print_result(executor.execute(FlakyTask(10), "retrain"))

    def bad_message() -> str:
        raise PermanentError("неверный формат сообщения")

    print("\n--- Неустранимая ошибка: повторов нет ---")
    _print_result(executor.execute(bad_message, "bad-message"))

    print("\nDead-letter очередь:")
    for letter in dlq.items:
        print(f"  {letter.task_name}: {letter.reason} (попыток: {letter.attempts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
