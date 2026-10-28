"""Run from the module directory after installing the local package."""

from igor_aggregation import (
    AverageAggregation, FinancialQueryService, MaxAggregation, SumAggregation,
)


def main() -> None:
    values = [100.0, 120.0, 140.0, 160.0]
    service = FinancialQueryService(AverageAggregation())
    print(f"values = {values}")
    print(f"average = {service.execute(values):g}")
    service.set_strategy(SumAggregation())
    print(f"sum = {service.execute(values):g}")
    service.set_strategy(MaxAggregation())
    print(f"max = {service.execute(values):g}")
    for invalid in ([], [float("nan")]):
        try:
            service.execute(invalid)
        except ValueError as error:
            print(f"rejected: {error}")


if __name__ == "__main__":
    main()
