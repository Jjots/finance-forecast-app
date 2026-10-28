"""Проверка: классы на диаграмме inference-classes.puml совпадают с кодом."""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import inference_comp
from inference_comp import context, errors, models, strategies, stubs

PUML = Path(__file__).resolve().parent.parent / "inference-classes.puml"
DECL = re.compile(r"^\s*(?:abstract\s+class|class|interface|enum)\s+(\w+)", re.MULTILINE)


def _classes_in_code() -> set[str]:
    found: set[str] = set()
    for module in (context, errors, models, strategies, stubs):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # _DriftFitted — приватная деталь имитации, на диаграмме её нет
            if obj.__module__ == module.__name__ and not name.startswith("_"):
                found.add(name)
    return found


def test_every_class_in_code_is_on_the_diagram_and_vice_versa() -> None:
    in_diagram = set(DECL.findall(PUML.read_text(encoding="utf-8")))
    in_code = _classes_in_code()
    assert in_code - in_diagram == set(), "есть в коде, нет на диаграмме"
    assert in_diagram - in_code == set(), "есть на диаграмме, нет в коде"


def test_strategies_implement_the_interface() -> None:
    for cls in (inference_comp.XGBoostStrategy, inference_comp.ARIMAStrategy):
        assert issubclass(cls, inference_comp.ForecastStrategy)
    assert hasattr(inference_comp.ForecastContext, "set_strategy")
    assert hasattr(inference_comp.ForecastContext, "predict")
