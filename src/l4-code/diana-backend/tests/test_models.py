from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

from forecast_comp import (
    MAX_HORIZON,
    ForecastRequest,
    ForecastResult,
    ForecastSource,
    InvalidForecastRequestError,
    InvalidMlResponseError,
)


def test_valid_request() -> None:
    request = ForecastRequest(company_id=100, horizon=12)
    assert (request.company_id, request.horizon) == (100, 12)


@pytest.mark.parametrize("company_id", [0, -1])
def test_company_id_must_be_positive(company_id: int) -> None:
    with pytest.raises(InvalidForecastRequestError):
        ForecastRequest(company_id=company_id, horizon=12)


@pytest.mark.parametrize("horizon", [0, -3, MAX_HORIZON + 1])
def test_horizon_out_of_range(horizon: int) -> None:
    with pytest.raises(InvalidForecastRequestError):
        ForecastRequest(company_id=1, horizon=horizon)


def test_bool_and_float_are_rejected() -> None:
    with pytest.raises(InvalidForecastRequestError):
        ForecastRequest(company_id=True, horizon=12)  # type: ignore[arg-type]
    with pytest.raises(InvalidForecastRequestError):
        ForecastRequest(company_id=1, horizon=12.0)  # type: ignore[arg-type]


def test_request_is_immutable() -> None:
    request = ForecastRequest(company_id=1, horizon=3)
    with pytest.raises(AttributeError):
        request.horizon = 5  # type: ignore[misc]


def test_result_length_must_match_horizon() -> None:
    with pytest.raises(InvalidMlResponseError):
        ForecastResult(1, 3, (1.0, 2.0), ForecastSource.ML, datetime.now(timezone.utc))


@pytest.mark.parametrize("bad", [math.nan, math.inf])
def test_result_rejects_non_finite(bad: float) -> None:
    with pytest.raises(InvalidMlResponseError):
        ForecastResult(1, 2, (1.0, bad), ForecastSource.ML, datetime.now(timezone.utc))
