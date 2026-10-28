import { ExportContext } from './ExportContext';
import { PdfExportStrategy } from './strategies/PdfExportStrategy';
import { ExcelExportStrategy } from './strategies/ExcelExportStrategy';
import { FinancialReport } from './models/FinancialReport';
import * as fs from 'fs';

async function main() {
    const report = new FinancialReport('ООО Ромашка', 2027, 1500000);

    const context = new ExportContext(new PdfExportStrategy());
    console.log('Exporting to PDF...');
    const pdfBlob = await context.executeExport(report);
    
    // Для демонстрации в Node.js конвертируем Blob в Buffer и сохраняем
    const pdfBuffer = Buffer.from(await pdfBlob.arrayBuffer());
    fs.writeFileSync('report.pdf', pdfBuffer);
    console.log(`PDF created (size: ${pdfBuffer.length} bytes)`);

    context.setStrategy(new ExcelExportStrategy());
    console.log('Exporting to Excel...');
    const excelBlob = await context.executeExport(report);
    
    const excelBuffer = Buffer.from(await excelBlob.arrayBuffer());
    fs.writeFileSync('report.xlsx', excelBuffer);
    console.log(`Excel created (size: ${excelBuffer.length} bytes)`);
}

main().catch(console.error);