"""Приёмник недоставленных сообщений (аналог dead-letter очереди RabbitMQ)."""

from __future__ import annotations

from typing import Protocol

from .models import DeadLetter


class DeadLetterSink(Protocol):
    """Куда executor отправляет задачу, которую не удалось выполнить."""

    def publish(self, letter: DeadLetter) -> None: ...


class InMemoryDeadLetterQueue:
    """Учебная реализация: хранит сообщения в памяти.

    В реальной системе это DLX + dead-letter queue в RabbitMQ.
    """

    def __init__(self) -> None:
        self._items: list[DeadLetter] = []

    def publish(self, letter: DeadLetter) -> None:
        self._items.append(letter)

    @property
    def items(self) -> tuple[DeadLetter, ...]:
        return tuple(self._items)
