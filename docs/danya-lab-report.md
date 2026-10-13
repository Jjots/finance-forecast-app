# Лабораторные работы №1–2. Даня: scheduler и queue

Репозиторий: https://github.com/Jjots/finance-forecast-app

Исходники диаграмм:

- `src/l1-context/danya-context.puml`
- `src/l2-containers/danya-containers.puml`
- `devops/danya-components-scheduler.puml`
- `devops/danya-components-queue.puml`

---

## 1. Роль и зона ответственности

Даня — DevOps + QA. Контейнеры: `scheduler` (Airflow / Celery Beat) и `queue` (RabbitMQ). Совместно с Игорем — эксплуатация `dwh` (TimescaleDB), но декомпозицию `dwh` делает Игорь.

Задача DevOps-контура: по расписанию забрать отчётность и рыночные данные, отдать их backend (`data_comp`) и асинхронно запустить переобучение ML через брокер, не блокируя API.

---

## 2. L1. Системный контекст

На L1 система — один блок `finance_forecast_system`. Внутри не видно ни backend, ни очереди.

Акторы:

| ID | Кто | Зачем системе |
|----|-----|----------------|
| `analyst` | Аналитик | Прогнозы и отчёты через веб |
| `investor` | Инвестор | Просмотры прогнозов с телефона |
| `risk_manager` | Риск-менеджер | Качество моделей и волатильность |
| `admin` | Администратор | Пользователи, ручные загрузки, запуск переобучения |

Внешние системы — это источники, которые качает планировщик:

| ID | Система | Протокол | Что забираем |
|----|---------|----------|--------------|
| `rfsd_dataset` | РСБУ (ИПП) | HTTPS/File | Отчётность 2011–2025, Parquet |
| `cbr_api` | ЦБ РФ | REST/HTTPS | Ставка, курсы, макро |
| `moex_api` | Московская биржа | REST/HTTPS | Котировки и индексы |

Пользователи ходят в систему по HTTPS. Система сама ходит наружу за данными. Очередь и Airflow на L1 не рисуем: это внутренности контейнерного уровня.

---

## 3. L2. Контейнеры

Ключевой контур Дани на L2:

1. `scheduler` забирает `rfsd_dataset` / `cbr_api` / `moex_api`.
2. `scheduler` отдаёт батч в `backend` по HTTPS/JSON (стыковка с `data_comp` на уровне компонентов).
3. `scheduler` публикует задачу переобучения в `queue` по AMQP.
4. `queue` доставляет задачу в `ml_service` по AMQP.
5. `ml_service` читает ряды из `dwh` по SQL/TCP.

Почему очередь, а не прямой вызов ML: обучение тяжёлое и не должно подвешивать FastAPI. AMQP даёт буфер, повтор и развязку по времени.

Связь `scheduler → backend` на L2 нужна, потому что в глоссарии `data_comp` ссылается со стороны `scheduler`: сырые файлы не пишутся в TimescaleDB напрямую из Airflow, а проходят через backend (валидация, upsert).

Остальные контейнеры (`web_app`, `mobile_app`, `db_main`) показаны, чтобы L2 была полной диаграммой системы, а не вырванным фрагментом.

---

## 4. Компоненты scheduler

Контейнер `scheduler` — один Python-процесс (Airflow Scheduler / Celery Beat). Пять компонентов в трёх слоях, внутренние связи — `Python Call`.

| Слой | ID | Ответственность |
|------|----|-----------------|
| Оркестрация | `schedule_comp` | Cron: ежедневный ingest, еженедельный retrain |
| Предметный | `ingest_comp` | Порядок источников, ошибка одного источника, повтор задания |
| Инфраструктура | `source_adapter_comp` | HTTPS/File и REST/HTTPS к внешним API |
| Инфраструктура | `backend_client_comp` | HTTPS/JSON к `data_comp` |
| Инфраструктура | `broker_publisher_comp` | AMQP к `connection_comp` |

Разделение ответственности: `schedule_comp` не знает URL ЦБ и формат Parquet. `ingest_comp` не открывает сокеты. Адаптеры не решают, когда запускать DAG.

### Спецификация внутренних интерфейсов scheduler

| От | К | Протокол | Контракт | Полезная нагрузка |
|----|---|----------|----------|-------------------|
| `schedule_comp` | `ingest_comp` | Python Call | `run_ingest(job_id, period)` | Идентификатор задания, интервал дат |
| `schedule_comp` | `broker_publisher_comp` | Python Call | `publish_retrain(job_id)` | Идентификатор задания переобучения |
| `ingest_comp` | `source_adapter_comp` | Python Call | `fetch_rfsd()`, `fetch_cbr()`, `fetch_moex()` | Сырой файл/JSON источника |
| `ingest_comp` | `backend_client_comp` | Python Call | `push_batch(job_id, payload)` | Нормализованный батч + статус |
| `backend_client_comp` | `data_comp` | HTTPS/JSON | `POST /internal/ingest` | JSON батча, идемпотентный `job_id` |
| `broker_publisher_comp` | `connection_comp` | AMQP | publish `ml.retrain` | `job_id`, причина запуска, timestamp |
| `source_adapter_comp` | `rfsd_dataset` | HTTPS/File | скачивание Parquet | Файл отчётности |
| `source_adapter_comp` | `cbr_api` | REST/HTTPS | GET макропоказателей | JSON ЦБ |
| `source_adapter_comp` | `moex_api` | REST/HTTPS | GET котировок | JSON MOEX |

---

## 5. Компоненты queue

Контейнер `queue` — процесс брокера RabbitMQ (одно адресное пространство). Четыре компонента. Снаружи AMQP, внутри по методичке `Python Call` (in-process вызовы модулей брокера).

| Слой | ID | Ответственность |
|------|----|-----------------|
| Вход | `connection_comp` | Соединения, каналы, vhost |
| Маршрутизация | `routing_comp` | Direct exchange, routing key |
| Хранение | `work_queue_comp` | Durable-очередь `ml.retrain` |
| Надёжность | `retry_comp` | TTL, redelivery, DLQ |

Поток: `scheduler` → `connection_comp` → `routing_comp` → `work_queue_comp` → `training_comp`. При nack: `work_queue_comp` → `retry_comp` → снова `routing_comp`. После лимита попыток сообщение остаётся в DLQ (внутри `retry_comp`), ML его больше не берёт.

Стыковка с ML: не абстрактный контейнер, а `training_comp` из глоссария.

### Спецификация внутренних интерфейсов queue

| От | К | Протокол | Контракт | Полезная нагрузка |
|----|---|----------|----------|-------------------|
| `scheduler` | `connection_comp` | AMQP | open channel + publish | Сообщение `ml.retrain` |
| `connection_comp` | `routing_comp` | Python Call | `route(exchange, routing_key, body)` | Конверт AMQP |
| `routing_comp` | `work_queue_comp` | Python Call | `enqueue(message)` | Задача переобучения |
| `work_queue_comp` | `training_comp` | AMQP | deliver, ждать ack | `job_id` |
| `work_queue_comp` | `retry_comp` | Python Call | `on_nack(message, attempt)` | Сообщение + номер попытки |
| `retry_comp` | `routing_comp` | Python Call | `requeue(message)` | Сообщение с увеличенным attempt |

---

## 6. Технологический стек (для опроса)

| Уровень | Технология | Зачем |
|---------|------------|--------|
| Планировщик | Airflow или Celery Beat | Расписание DAG/beat, а не crontab на сервере |
| Язык планировщика | Python | Единый стек с backend и ML, in-process `Python Call` |
| HTTP-клиент | httpx | HTTPS/File и REST/HTTPS к РСБУ, ЦБ, MOEX и к backend |
| Брокер | RabbitMQ | Классические задачи (не лог-стрим), ack, TTL, DLQ |
| Протокол брокера | AMQP 0-9-1 | Публикация и доставка `ml.retrain` |
| AMQP-клиент | aio-pika | Публикация из Python-процесса scheduler |
| Backend | Python + FastAPI | `data_comp` принимает батч |
| ML | XGBoost + ARIMA | Потребитель очереди (`training_comp`) |
| DWH | TimescaleDB | Ряды; пишет backend, читает ML |
| Основная БД | PostgreSQL | Пользователи и метаданные, не зона ingest |
| Клиенты | React / React Native | До scheduler не доходят |

Почему RabbitMQ, а не Kafka: объём — редкие задания переобучения, нужны очереди задач с ack и DLQ, а не шина событий с ретеншеном.

Почему не вызывать ML по REST из scheduler: обучение минуты и часы; HTTP-timeout и ретраи на уровне API хуже, чем брокер.

Почему данные в backend, а не сразу в `dwh`: валидация, нормализация единиц и идемпотентный upsert живут в `data_comp`. Scheduler не дублирует бизнес-правила хранения.

---

## 7. Шпаргалка к опросу Бычкова

**Что делает твоя часть.** По расписанию качаю РСБУ, ЦБ и MOEX, отдаю батч в `data_comp`, раз в неделю кладу в RabbitMQ задачу `ml.retrain`. Backend и UI от этого не блокируются.

**L1 vs L2 vs компоненты.** L1 — люди и внешние системы вокруг всей ИС. L2 — контейнеры, мой контур `scheduler` и `queue`. Компоненты — модули внутри одного процесса.

**Единое адресное пространство.** У scheduler это один Python-процесс: вызовы функций, не сеть. У queue — один процесс брокера. Сеть начинается на границе контейнера: HTTPS/JSON, REST/HTTPS, HTTPS/File, AMQP.

**Слои scheduler.** Расписание / сценарий загрузки / адаптеры. Если ЦБ сменит URL, меняется только `source_adapter_comp`.

**Стыковочные ID.** На backend я бью в `data_comp`, не в «весь backend». На ML очередь бьёт в `training_comp`, не в инференс.

**Идемпотентность.** Повтор того же `job_id` не должен плодить дубли в DWH: это гарантирует `data_comp`; scheduler передаёт стабильный ключ задания.

**Падение ML.** Сообщение не ack — `retry_comp` вернёт его в маршрутизацию. После лимита — DLQ, алерт QA, API продолжает отдавать старый прогноз.

**Протоколы на связях.** Внутри контейнера только `Python Call`. Наружу только из списка методички. Макросы `Rel_D/R/L/U` и `skinparam` не используются. Все ID из `docs/glossary.md`.
