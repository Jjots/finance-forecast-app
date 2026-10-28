"""Прототип компонента retry_comp (контейнер queue): повторы со Strategy."""

from .dead_letter import DeadLetterSink, InMemoryDeadLetterQueue
from .errors import PermanentError
from .executor import RetryExecutor
from .models import DeadLetter, RetryResult, RetryStatus
from .strategies import ExponentialBackoffStrategy, FixedDelayStrategy, RetryStrategy

__all__ = [
    "DeadLetter",
    "DeadLetterSink",
    "ExponentialBackoffStrategy",
    "FixedDelayStrategy",
    "InMemoryDeadLetterQueue",
    "PermanentError",
    "RetryExecutor",
    "RetryResult",
    "RetryStatus",
    "RetryStrategy",
]
