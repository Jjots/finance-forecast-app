"""Behavior, replacement, validation and numerical boundary tests."""

from dataclasses import FrozenInstanceError
import unittest
from typing import cast

from igor_aggregation import (
    AggregationStrategy, AverageAggregation, FinancialQueryService,
    FinancialTimeSeries, MaxAggregation, SumAggregation,
)


class ConstantAggregation:
    """Independent structural implementation: no service modification needed."""

    def execute(self, series: FinancialTimeSeries) -> float:
        return float(len(series.values))


class AggregationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.strategies: tuple[AggregationStrategy, ...] = (
            SumAggregation(), AverageAggregation(), MaxAggregation(),
        )

    def test_reference_example_and_runtime_replacement(self) -> None:
        service = FinancialQueryService(AverageAggregation())
        values = [100.0, 120.0, 140.0, 160.0]
        self.assertEqual(service.execute(values), 130.0)
        service.set_strategy(SumAggregation())
        self.assertEqual(service.execute(values), 520.0)
        service.set_strategy(MaxAggregation())
        self.assertEqual(service.execute(values), 160.0)

    def test_common_contract(self) -> None:
        cases = [
            ([7.5], (7.5, 7.5, 7.5)),
            ([-4.0, -2.0, -6.0], (-12.0, -4.0, -2.0)),
            ([0.0, 0.0], (0.0, 0.0, 0.0)),
            ([0.1, 0.2, 0.3], (0.6, 0.2, 0.3)),
            ([-3.0, 0.0, 6.0], (3.0, 1.0, 6.0)),
        ]
        for values, expected in cases:
            for strategy, result in zip(self.strategies, expected):
                with self.subTest(values=values, strategy=type(strategy).__name__):
                    self.assertAlmostEqual(FinancialQueryService(strategy).execute(values), result)

    def test_empty_rejected_by_all_strategies(self) -> None:
        for strategy in self.strategies:
            with self.subTest(strategy=type(strategy).__name__), self.assertRaises(ValueError):
                FinancialQueryService(strategy).execute([])

    def test_non_finite_values_rejected(self) -> None:
        for strategy in self.strategies:
            for value in (float("nan"), float("inf"), -float("inf")):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    FinancialQueryService(strategy).execute([value])

    def test_non_numeric_and_bool_rejected(self) -> None:
        for strategy in self.strategies:
            for value in ("100", None, True, False):
                with self.subTest(value=value), self.assertRaises(TypeError):
                    FinancialQueryService(strategy).execute(cast(list[float], [value]))

    def test_input_unchanged_and_tuple_accepted(self) -> None:
        values = [100.0, 120.0]
        for strategy in self.strategies:
            FinancialQueryService(strategy).execute(values)
            self.assertEqual(values, [100.0, 120.0])
            self.assertIsInstance(FinancialQueryService(strategy).execute(tuple(values)), float)

    def test_model_snapshots_and_is_immutable(self) -> None:
        original = [1.0, 2.0]
        series = FinancialTimeSeries(tuple(original))
        original.append(3.0)
        self.assertEqual(series.values, (1.0, 2.0))
        with self.assertRaises(FrozenInstanceError):
            setattr(series, "values", (99.0,))

    def test_extension_without_changing_service(self) -> None:
        service = FinancialQueryService(SumAggregation())
        service.set_strategy(ConstantAggregation())
        self.assertEqual(service.execute([4.0, 8.0, 9.0]), 3.0)

    def test_invalid_call_does_not_break_later_call(self) -> None:
        service = FinancialQueryService(SumAggregation())
        with self.assertRaises(ValueError):
            service.execute([])
        self.assertEqual(service.execute([2.0, 3.0]), 5.0)

    def test_finite_large_mean(self) -> None:
        self.assertEqual(FinancialQueryService(AverageAggregation()).execute([1e308, 1e308]), 1e308)

    def test_sum_overflow_is_explicit(self) -> None:
        with self.assertRaises(OverflowError):
            FinancialQueryService(SumAggregation()).execute([1e308, 1e308])

    def test_accurate_sum_with_cancellation(self) -> None:
        self.assertEqual(FinancialQueryService(SumAggregation()).execute([1e16, 1.0, -1e16]), 1.0)

    def test_integer_observations(self) -> None:
        self.assertEqual(FinancialQueryService(SumAggregation()).execute([100, 120, 140, 160]), 520.0)


if __name__ == "__main__":
    unittest.main()
