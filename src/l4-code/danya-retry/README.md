# L4 · retry_comp (контейнер queue) · паттерн Strategy

Учебный прототип компонента **`retry_comp`** из L3-диаграммы контейнера `queue` (RabbitMQ):
повторное выполнение неуспешной задачи с выбираемым алгоритмом паузы.

| | |
|---|---|
| Контейнер / компонент | `queue` / `retry_comp` |
| Стратегии | `FixedDelayStrategy` (2, 2, 2 c), `ExponentialBackoffStrategy` (2, 4, 8 c) |
| Контекст | `RetryExecutor` |
| Язык | Python 3.10+ (строгая типизация, проверяется `mypy --strict`) |
| Диаграмма классов | [`retry-classes.puml`](retry-classes.puml) |

## Установка

```bash
cd src/l4-code/danya-retry
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

Для запуска самого прототипа сторонние библиотеки не нужны, только стандартная.

## Запуск демонстрации

```bash
# Linux / macOS
PYTHONPATH=src python -m retry_comp.demo          # паузы имитируются, мгновенно
PYTHONPATH=src python -m retry_comp.demo --real   # настоящие паузы time.sleep

# Windows (PowerShell)
$env:PYTHONPATH="src"; python -m retry_comp.demo
```

Демонстрация показывает: задачу, которая падает дважды и проходит с третьей попытки
(для обеих стратегий), смену стратегии на лету, исчерпание лимита попыток и неустранимую
ошибку. Пример вывода: [`demo_output.txt`](demo_output.txt).

## Тесты и проверка типов

```bash
python -m pytest -v        # 26 тестов, паузы подменены, выполняются мгновенно
python -m mypy --strict src tests
```

В тестах есть положительные сценарии (успех, успех после двух сбоев, смена стратегии) и
отрицательные (исчерпание попыток, `PermanentError`, неверные параметры, попытка создать
интерфейс).

## Структура

```
danya-retry/
├── retry-classes.puml           UML-диаграмма классов (PlantUML)
├── src/retry_comp/
│   ├── strategies.py            RetryStrategy, FixedDelayStrategy, ExponentialBackoffStrategy
│   ├── executor.py              RetryExecutor (контекст Strategy)
│   ├── models.py                RetryResult, RetryStatus, DeadLetter
│   ├── dead_letter.py           DeadLetterSink, InMemoryDeadLetterQueue
│   ├── errors.py                PermanentError
│   └── demo.py                  демонстрационный запуск
└── tests/                       pytest
```

## Пример использования

```python
from retry_comp import RetryExecutor, FixedDelayStrategy, ExponentialBackoffStrategy

executor = RetryExecutor(FixedDelayStrategy(delay=2), max_attempts=3)
result = executor.execute(task)                     # паузы 2, 2
executor.set_strategy(ExponentialBackoffStrategy(base_delay=2))
result = executor.execute(task)                     # паузы 2, 4
```

## Связь с L3 и RabbitMQ

В L3 `retry_comp` (TTL + DLQ) получает от `work_queue_comp` сообщение при nack или
истечении TTL и возвращает его в `routing_comp`. В прототипе:

| Реальная система (RabbitMQ) | Прототип |
|---|---|
| пауза перед повторной доставкой (TTL сообщения в retry-очереди) | `RetryStrategy.execute()` + `sleep` |
| лимит попыток (счётчик доставок, заголовок `x-death`) | `max_attempts` |
| dead-letter exchange и очередь для отклонённых | `DeadLetterSink` / `InMemoryDeadLetterQueue` |
| сообщение, которое повторять нельзя | `PermanentError` |

## Ограничения учебного прототипа

- RabbitMQ не запускается: брокер, очереди и TTL не воспроизводятся, имитируется только
  логика повторов и выбора паузы.
- Выполнение синхронное, в одном потоке; в брокере повторы делаются без блокировки
  потребителя (сообщение ждёт в retry-очереди).
- Dead-letter очередь хранится в памяти и не переживает перезапуск.
- Случайный разброс паузы (jitter) не реализован.
