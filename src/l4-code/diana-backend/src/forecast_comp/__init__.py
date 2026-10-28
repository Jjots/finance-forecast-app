"""forecast_comp — компонент «Прогнозы» backend (L4, Strategy)."""

from .errors import (
    CacheMissError,
    ForecastError,
    InvalidForecastRequestError,
    InvalidMlResponseError,
    MlServiceUnavailableError,
)
from .models import MAX_HORIZON, ForecastRequest, ForecastResult, ForecastSource
from .ports import ForecastCacheReader, ForecastCacheWriter, MlClient
from .service import ForecastService
from .strategies import (
    CachedForecastStrategy,
    FallbackForecastStrategy,
    ForecastRetrievalStrategy,
    MlForecastStrategy,
)

__all__ = [
    "CacheMissError",
    "CachedForecastStrategy",
    "FallbackForecastStrategy",
    "ForecastCacheReader",
    "ForecastCacheWriter",
    "ForecastError",
    "ForecastRequest",
    "ForecastResult",
    "ForecastRetrievalStrategy",
    "ForecastService",
    "ForecastSource",
    "InvalidForecastRequestError",
    "InvalidMlResponseError",
    "MAX_HORIZON",
    "MlClient",
    "MlForecastStrategy",
    "MlServiceUnavailableError",
]
