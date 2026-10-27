# L4: inference_comp (ml_service) — Диана

Прототип компонента `inference_comp` контейнера `ml_service` (L3: «Inference Component»).
Паттерн **Strategy** позволяет подменять модель прогнозирования (XGBoost или ARIMA) при едином интерфейсе для клиента.

## Состав

| Файл | Назначение |
|---|---|
| `inference-classes.puml` | UML Class Diagram (PlantUML) |
| `src/inference_comp/models.py` | `TimeSeriesData`, `PredictionResult`, `validate_horizon` |
| `src/inference_comp/features.py` | лаговые признаки для XGBoost (роль feature_engineer_comp) |
| `src/inference_comp/strategies.py` | `ForecastStrategy`, `XGBoostStrategy`, `ARIMAStrategy` |
| `src/inference_comp/context.py` | контекст `ForecastContext` |
| `src/inference_comp/stubs.py` | **имитации** моделей (не обученные XGBoost/ARIMA) |
| `src/inference_comp/demo.py` | демонстрационный запуск |
| `tests/` | pytest-тесты (включая проверку «диаграмма = код») |

## Установка и запуск

Требуется Python 3.10+.

```bash
cd src/l4-code/diana-ml
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                      # numpy, xgboost, statsmodels, pytest

PYTHONPATH=src python -m inference_comp.demo          # настоящие XGBoost и ARIMA
PYTHONPATH=src python -m inference_comp.demo --stub   # имитации, без xgboost/statsmodels
python -m pytest -v -rs                               # тесты
```

Windows (PowerShell): `$env:PYTHONPATH="src"; python -m inference_comp.demo`

Без установленных `xgboost`/`statsmodels` тесты на настоящих моделях (`tests/test_real_models.py`)
пропускаются, остальные выполняются на имитациях.

## Пример использования

```python
context = ForecastContext(XGBoostStrategy(n_lags=3))
prediction_1 = context.predict(data, horizon=3)
context.set_strategy(ARIMAStrategy(order=(1, 1, 1)))
prediction_2 = context.predict(data, horizon=3)
```

## Ограничения учебного прототипа

- Модель обучается на переданном ряду при каждом вызове. В целевой системе `inference_comp` загружает **уже обученную** активную модель из `model_registry_comp`, обучение выполняет `training_comp`.
- Лаговые признаки строятся в `features.py`; полноценный `feature_engineer_comp` (скользящие средние, темпы роста, макро-признаки) не реализован.
- `stubs.py` — имитации с тем же интерфейсом; их числа не отражают качество реальных моделей. Режим `--stub` и тесты на имитациях проверяют логику паттерна, а не точность прогноза.
- Данные в `demo.py` — условный тестовый ряд, не реальная отчётность.
