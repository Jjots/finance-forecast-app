# L4: export_service (web_app)

Реализация паттерна **Strategy** для экспорта финансовых прогнозов в форматы PDF и Excel.

## Установка

pm install

## Запуск демо

pm start

## Тесты

pm test

## Архитектура
- FinancialReport: модель данных.
- ExportStrategy: интерфейс стратегии.
- PdfExportStrategy: экспорт в PDF (заглушка).
- ExcelExportStrategy: экспорт в Excel (заглушка).
- ExportContext: контекст, переключающий стратегии.
