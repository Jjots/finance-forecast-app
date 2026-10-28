import { ExportContext } from './ExportContext';
import { PdfExportStrategy } from './strategies/PdfExportStrategy';
import { ExcelExportStrategy } from './strategies/ExcelExportStrategy';
import { FinancialReport } from './models/FinancialReport';

async function main() {
    const report = new FinancialReport('ООО Ромашка', 2027, 1500000);

    const context = new ExportContext(new PdfExportStrategy());
    console.log('Exporting to PDF...');
    const pdfFile = await context.executeExport(report);
    console.log(`PDF created (size: ${pdfFile.length} bytes)`);

    context.setStrategy(new ExcelExportStrategy());
    console.log('Exporting to Excel...');
    const excelFile = await context.executeExport(report);
    console.log(`Excel created (size: ${excelFile.length} bytes)`);
}

main().catch(console.error);
