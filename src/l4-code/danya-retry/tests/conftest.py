"""Общие заготовки тестов."""

from __future__ import annotations

import pytest


class FakeSleep:
    """Подменяет time.sleep: запоминает паузы и не ждёт."""

    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


class FlakyTask:
    """Падает первые ``failures`` вызовов, затем возвращает ``"ok"``."""

    def __init__(self, failures: int) -> None:
        self.failures = failures
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError(f"сбой {self.calls}")
        return "ok"


@pytest.fixture
def fake_sleep() -> FakeSleep:
    return FakeSleep()
