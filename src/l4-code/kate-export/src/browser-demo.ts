import { ExportContext } from './ExportContext';
import { PdfExportStrategy } from './strategies/PdfExportStrategy';
import { ExcelExportStrategy } from './strategies/ExcelExportStrategy';
import { FinancialReport } from './models/FinancialReport';

/**
 * Демонстрационный скрипт для запуска в браузере.
 * В реальном React-приложении этот код будет вызываться по нажатию кнопки.
 */
export async function downloadFile(blob: Blob, filename: string): Promise<void> {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

export async function runBrowserDemo(): Promise<void> {
    const report = new FinancialReport('ООО Ромашка', 2027, 1500000);

    // Экспорт в PDF
    const pdfContext = new ExportContext(new PdfExportStrategy());
    const pdfBlob = await pdfContext.export(report);
    await downloadFile(pdfBlob, 'report.pdf');
    console.log(`PDF скачан (размер: ${pdfBlob.size} байт)`);

    // Экспорт в Excel
    pdfContext.setStrategy(new ExcelExportStrategy());
    const excelBlob = await pdfContext.export(report);
    await downloadFile(excelBlob, 'report.xlsx');
    console.log(`Excel скачан (размер: ${excelBlob.size} байт)`);
}