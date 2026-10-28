import { ExportContext } from './ExportContext';
import { PdfExportStrategy } from './strategies/PdfExportStrategy';
import { ExcelExportStrategy } from './strategies/ExcelExportStrategy';
import { FinancialReport } from './models/FinancialReport';

// Тестовые данные
const report = new FinancialReport('ООО Ромашка', 2027, 1500000);
const context = new ExportContext(new PdfExportStrategy());

// Функция для скачивания Blob
function downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Обработчик PDF
document.getElementById('btn-pdf')?.addEventListener('click', async () => {
    context.setStrategy(new PdfExportStrategy());
    const blob = await context.export(report);
    downloadBlob(blob, 'report.pdf');
    console.log(`PDF скачан (размер: ${blob.size} байт)`);
});

// Обработчик Excel
document.getElementById('btn-excel')?.addEventListener('click', async () => {
    context.setStrategy(new ExcelExportStrategy());
    const blob = await context.export(report);
    downloadBlob(blob, 'report.xlsx');
    console.log(`Excel скачан (размер: ${blob.size} байт)`);
});