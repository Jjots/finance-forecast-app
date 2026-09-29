# Правила работы с репозиторием

## Ветки

Все изменения — только через feature-ветки. В `main` напрямую не пушим.

| Тип | Формат | Пример |
|---|---|---|
| Новая функциональность | `feature/имя-задача` | `feature/kate-l1-context` |
| Исправление | `bugfix/имя-задача` | `bugfix/fix-puml-syntax` |
| Документация | `docs/имя-задача` | `docs/update-glossary` |

## Цикл работы

1. Обновить main:

git checkout main
git pull origin main


2. Создать ветку:

git checkout -b feature/имя-задача


3. Работать, коммитить:

git add .
git commit -m "feat: описание"


4. Запушить свою ветку:

git push origin feature/имя-задача


5. Открыть Pull Request на GitHub.

6. Дождаться Code Review (минимум 1 аппрув).

7. Merge PR → удалить ветку.

8. Обновить main:

git checkout main
git pull origin main


## Commit messages

Формат: `тип: описание`

| Тип         | Когда                   
| `feat:`     | новая функциональность 
| `fix:`      | исправление       
| `docs:`     | документация      
| `chore:`    | рутина, структура
| `refactor:` | рефакторинг       

Примеры:
- `feat: add Kate L1 context diagram`
- `fix: correct protocol in container diagram`
- `docs: update glossary with new IDs`

## PlantUML — правила

1. Только макрос `Rel(...)` — без `Rel_D/R/L/U`.
2. Без `skinparam` в файлах разработчиков (только в `main.puml`).
3. Все ID — из `docs/glossary.md`. Не выдумывать свои.
4. На каждой связи — протокол (`HTTPS/JSON`, `SQL/TCP`, `AMQP`, `gRPC`).
5. Файлы кладём:
- L1 → `src/l1-context/имя-context.puml`
- L2 → `src/l2-containers/имя-containers.puml`

## Code Review

- Автор PR не может сам себя аппрувить.
- Аппрув делает тимлид (Алиса) или другой участник.
- Комментарии обязательны — хотя бы один осмысленный.
- Если CI упал — исправить, потом снова запросить ревью.

## Запрещено

- ❌ Прямой push в `main`.
- ❌ Force push в `main`.
- ❌ Мерж PR без аппрува.
- ❌ Использование ID, которых нет в глоссарии.