"""Проверка: классы на диаграмме forecast-classes.puml совпадают с кодом."""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import forecast_comp
from forecast_comp import errors, fakes, models, ports, service, strategies

PUML = Path(__file__).resolve().parent.parent / "forecast-classes.puml"
DECL = re.compile(r"^\s*(?:abstract\s+class|class|interface|enum)\s+(\w+)", re.MULTILINE)


def _classes_in_code() -> set[str]:
    found: set[str] = set()
    for module in (errors, fakes, models, ports, service, strategies):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                found.add(name)
    return found


def test_every_class_in_code_is_on_the_diagram_and_vice_versa() -> None:
    in_diagram = set(DECL.findall(PUML.read_text(encoding="utf-8")))
    in_code = _classes_in_code()
    assert in_code - in_diagram == set(), "есть в коде, нет на диаграмме"
    assert in_diagram - in_code == set(), "есть на диаграмме, нет в коде"


def test_strategy_methods_match_diagram() -> None:
    text = PUML.read_text(encoding="utf-8")
    assert "ForecastService" in text and "set_strategy" in text
    assert hasattr(forecast_comp.ForecastService, "set_strategy")
    assert hasattr(forecast_comp.ForecastService, "get_forecast")
    for cls in (
        forecast_comp.CachedForecastStrategy,
        forecast_comp.MlForecastStrategy,
        forecast_comp.FallbackForecastStrategy,
    ):
        assert issubclass(cls, forecast_comp.ForecastRetrievalStrategy)
