import { ExportContext } from './ExportContext';
import { PdfExportStrategy } from './strategies/PdfExportStrategy';
import { ExcelExportStrategy } from './strategies/ExcelExportStrategy';
import { FinancialReport } from './models/FinancialReport';

async function main() {
    const report = new FinancialReport('ООО Ромашка', 2027, 1500000);
    const context = new ExportContext(new PdfExportStrategy());

    console.log('--- Демонстрация в Node.js (Blob создается, размер выводится) ---');
    
    const pdfBlob = await context.export(report);
    console.log(`PDF создан (размер: ${pdfBlob.size} байт, тип: ${pdfBlob.type})`);

    context.setStrategy(new ExcelExportStrategy());
    const excelBlob = await context.export(report);
    console.log(`Excel создан (размер: ${excelBlob.size} байт, тип: ${excelBlob.type})`);
    
    console.log('\nДля скачивания в браузере откройте demo.html после сборки (npm run build:demo)');
}

main().catch(console.error);