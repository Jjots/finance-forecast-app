"""Стратегии вычисления паузы между повторами (паттерн Strategy)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class RetryStrategy(ABC):
    """Общий контракт: по номеру повтора вернуть паузу в секундах.

    Номер повтора считается с 1: ``1`` - пауза после первой неудачной попытки.
    """

    @abstractmethod
    def execute(self, retry_number: int) -> float:
        """Вернуть паузу (секунды, не меньше 0) перед повтором номер ``retry_number``."""

    @staticmethod
    def _check_retry_number(retry_number: int) -> None:
        if retry_number < 1:
            raise ValueError(f"retry_number должен быть >= 1, получено {retry_number}")


class FixedDelayStrategy(RetryStrategy):
    """Постоянная пауза: 2, 2, 2, ... секунд."""

    def __init__(self, delay: float = 2.0) -> None:
        if delay < 0:
            raise ValueError("delay не может быть отрицательным")
        self._delay = delay

    def execute(self, retry_number: int) -> float:
        self._check_retry_number(retry_number)
        return self._delay


class ExponentialBackoffStrategy(RetryStrategy):
    """Пауза растёт в ``factor`` раз: 2, 4, 8, ... секунд (с необязательным потолком)."""

    def __init__(
        self,
        base_delay: float = 2.0,
        factor: float = 2.0,
        max_delay: Optional[float] = None,
    ) -> None:
        if base_delay < 0:
            raise ValueError("base_delay не может быть отрицательным")
        if factor < 1:
            raise ValueError("factor должен быть >= 1")
        if max_delay is not None and max_delay < 0:
            raise ValueError("max_delay не может быть отрицательным")
        self._base_delay = base_delay
        self._factor = factor
        self._max_delay = max_delay

    def execute(self, retry_number: int) -> float:
        self._check_retry_number(retry_number)
        delay = self._base_delay * self._factor ** (retry_number - 1)
        if self._max_delay is not None:
            delay = min(delay, self._max_delay)
        return delay
