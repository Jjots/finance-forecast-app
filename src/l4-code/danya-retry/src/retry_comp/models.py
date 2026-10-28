"""Модели данных компонента retry_comp."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class RetryStatus(Enum):
    """Итог выполнения задачи с повторами."""

    SUCCESS = "success"
    EXHAUSTED = "exhausted"  # лимит попыток исчерпан
    PERMANENT_FAILURE = "permanent_failure"  # неустранимая ошибка


@dataclass(frozen=True)
class RetryResult(Generic[T]):
    """Результат выполнения: статус, значение, число попыток, паузы и ошибки."""

    status: RetryStatus
    value: Optional[T]
    attempts: int
    delays: tuple[float, ...]
    errors: tuple[str, ...]

    @property
    def succeeded(self) -> bool:
        return self.status is RetryStatus.SUCCESS


@dataclass(frozen=True)
class DeadLetter:
    """Сообщение, попавшее в dead-letter очередь."""

    task_name: str
    reason: str
    attempts: int
