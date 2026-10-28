# ЛР №3 — Игорь: агрегация временных рядов

Компонент `dwh_query_comp` контейнера `dwh`. Python ООП-прототип паттерна Strategy: сумма, среднее, максимум. Основание: ТЗ версии 1.0 от 26.10.2026, разделы 1, 4, 8–10.

## Установка и запуск

Python 3.11+; внешних зависимостей для демонстрации и тестов нет. Команды выполняются из этой папки (`src/l4-code/igor-aggregation`).

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python demo.py
.venv\Scripts\python -m unittest discover -s tests -v
.venv\Scripts\python -m mypy --strict src demo.py tests
```

Linux/macOS: вместо `.venv\Scripts\python` использовать `.venv/bin/python`. Для установки dev-зависимости mypy нужен доступ к PyPI. Для запуска без установки и без интернета в PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python demo.py
python -m unittest discover -s tests -v
```

Ожидаемый вывод:

```text
values = [100.0, 120.0, 140.0, 160.0]
average = 130
sum = 520
max = 160
rejected: Time series must not be empty
rejected: Each observation must be finite
```

## Контракт

`FinancialQueryService(strategy).execute(values: Sequence[float]) -> float` создаёт неизменяемый `FinancialTimeSeries` и передаёт его выбранной стратегии. `set_strategy(strategy)` меняет алгоритм на том же экземпляре сервиса. Стратегии реализуют `AggregationStrategy` структурно через `typing.Protocol`.

| Ситуация | Поведение |
|---|---|
| Конечные int/float | Нормализация в float, вычисление |
| Пустой набор, NaN, ±inf | ValueError для всех стратегий |
| bool, str, None | TypeError; не преобразуем строки в числа |
| Сумма не помещается во float | OverflowError |
| Один элемент | Его значение для всех стратегий |
| Отрицательные/нулевые значения | Допустимы |

Арифметика float приблизительна: суммы используют `math.fsum`, среднее масштабирует значения, чтобы избежать переполнения промежуточной суммы. Возможны округление и потеря очень малых значений; это не расчёт бухгалтерских сумм с фиксированной точностью. Нужные для промышленного решения Decimal/NUMERIC не имитируются. Большие Python int, не представимые во float, дают OverflowError при преобразовании.

Входной список не меняется. Ряд уже выбран для одной компании, показателя, валюты и периода; смешивание несопоставимых показателей не контролируется. Временные метки и SQL-фильтрация находятся за пределами прототипа. При совместном использовании контекста из разных потоков нужна внешняя синхронизация смены стратегии.

## Файлы

- `src/igor_aggregation/models.py`: неизменяемые данные и проверка входа.
- `strategies.py`: Protocol и три алгоритма.
- `service.py`: контекст и замена алгоритма.
- `demo.py`: контрольный пример ТЗ и ошибки.
- `tests/test_aggregation.py`: 13 тестов, включая общие контракты и независимую новую стратегию.
- `aggregation-classes.puml`, `.png`, `.svg`: исходник и рендер UML.

## UML

```text
java -jar plantuml.jar -checkonly aggregation-classes.puml
java -jar plantuml.jar -tpng aggregation-classes.puml
java -jar plantuml.jar -tsvg aggregation-classes.puml
```

Проверено PlantUML 1.2026.2 (java8 artifact); Smetana встроена, Graphviz не нужен. PNG/SVG уже включены. Диаграмма L4 использует обычные отношения UML по разделу 8 ТЗ: пунктирный полый треугольник — реализация интерфейса, стрелка от контекста — использование, пунктирная зависимость — создание/тип входа. Классы L4 не являются новыми C4 ID.

## Связь с архитектурой проекта

Компонент dwh_query_comp относится к контейнеру dwh (TimescaleDB) и отвечает за агрегацию финансовых временных рядов. В рамках ЛР №3 реализован независимый Python-прототип, демонстрирующий применение паттерна Strategy. Подключение к реальной базе данных не предусмотрено. В целевой системе аналогичные операции выполняются средствами SQL (SUM, AVG, MAX).
