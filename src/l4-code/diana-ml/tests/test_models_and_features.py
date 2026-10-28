from __future__ import annotations

import math

import numpy as np
import pytest

from inference_comp import (
    MAX_HORIZON,
    InsufficientDataError,
    InvalidHorizonError,
    InvalidTimeSeriesError,
    PredictionResult,
    TimeSeriesData,
    validate_horizon,
)
from inference_comp.features import make_lag_matrix


def test_time_series_coerces_to_floats_tuple() -> None:
    data = TimeSeriesData.from_sequence([1, 2, 3])
    assert data.values == (1.0, 2.0, 3.0)
    assert len(data) == 3


def test_empty_series_rejected() -> None:
    with pytest.raises(InvalidTimeSeriesError):
        TimeSeriesData.from_sequence([])


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_non_finite_series_rejected(bad: float) -> None:
    with pytest.raises(InvalidTimeSeriesError):
        TimeSeriesData.from_sequence([1.0, bad])


def test_non_numeric_series_rejected() -> None:
    with pytest.raises(InvalidTimeSeriesError):
        TimeSeriesData(values=("a", "b"))  # type: ignore[arg-type]


@pytest.mark.parametrize("horizon", [0, -1, MAX_HORIZON + 1])
def test_validate_horizon_rejects_out_of_range(horizon: int) -> None:
    with pytest.raises(InvalidHorizonError):
        validate_horizon(horizon)


def test_validate_horizon_rejects_bool_and_float() -> None:
    with pytest.raises(InvalidHorizonError):
        validate_horizon(True)  # type: ignore[arg-type]
    with pytest.raises(InvalidHorizonError):
        validate_horizon(3.0)  # type: ignore[arg-type]


def test_prediction_result_length_must_match_horizon() -> None:
    with pytest.raises(InvalidHorizonError):
        PredictionResult(horizon=3, values=(1.0, 2.0), model_name="x")


def test_lag_matrix_shape_and_values() -> None:
    x, y = make_lag_matrix([1.0, 2.0, 3.0, 4.0, 5.0], n_lags=2)
    assert x.shape == (3, 2)
    assert np.array_equal(x, [[1, 2], [2, 3], [3, 4]])
    assert np.array_equal(y, [3, 4, 5])


def test_lag_matrix_needs_more_points_than_lags() -> None:
    with pytest.raises(InsufficientDataError):
        make_lag_matrix([1.0, 2.0, 3.0], n_lags=3)


def test_lag_matrix_rejects_bad_n_lags() -> None:
    with pytest.raises(ValueError):
        make_lag_matrix([1.0, 2.0, 3.0], n_lags=0)
