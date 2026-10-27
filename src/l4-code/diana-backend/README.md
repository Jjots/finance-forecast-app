# L4: forecast_comp (backend) — Диана

Прототип компонента `forecast_comp` контейнера `backend` (L3: «Прогнозы»).
Паттерн **Strategy** выбирает источник прогноза: сохранённый результат или новый расчёт через ML-клиент.

## Состав

| Файл | Назначение |
|---|---|
| `forecast-classes.puml` | UML Class Diagram (PlantUML) |
| `src/forecast_comp/models.py` | `ForecastRequest`, `ForecastResult`, `ForecastSource` |
| `src/forecast_comp/ports.py` | порты: `ForecastCacheReader/Writer` (db_repo_comp), `MlClient` (ml_client_comp) |
| `src/forecast_comp/strategies.py` | `ForecastRetrievalStrategy`, `CachedForecastStrategy`, `MlForecastStrategy`, `FallbackForecastStrategy` |
| `src/forecast_comp/service.py` | контекст `ForecastService` |
| `src/forecast_comp/fakes.py` | **имитаторы** кэша и ML-клиента (для демо и тестов) |
| `src/forecast_comp/demo.py` | демонстрационный запуск |
| `tests/` | pytest-тесты (включая проверку «диаграмма = код») |

## Установка и запуск

Требуется Python 3.10+. Внешних зависимостей, кроме pytest, нет.

```bash
cd src/l4-code/diana-backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

PYTHONPATH=src python -m forecast_comp.demo          # демонстрация
python -m pytest -v                                  # тесты
```

Windows (PowerShell): `$env:PYTHONPATH="src"; python -m forecast_comp.demo`

## Пример использования

```python
request = ForecastRequest(company_id=100, horizon=12)
service = ForecastService(CachedForecastStrategy(cache))
first = service.get_forecast(request)                # из кэша
service.set_strategy(MlForecastStrategy(ml_client))
second = service.get_forecast(request)               # новый расчёт ML
```

## Ограничения учебного прототипа

- Кэш и ML-клиент — **имитаторы** (`fakes.py`); реальных обращений к PostgreSQL и `ml_service` нет, значения прогноза тестовые.
- XGBoost и ARIMA в backend не переносятся: модели остаются в `ml_service`.
- `FallbackForecastStrategy` показывает целевое поведение L3 («при недоступности ML отдаём последний сохранённый прогноз»); circuit breaker, таймауты и повторы относятся к `ml_client_comp` и здесь не реализованы.
