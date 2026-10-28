import { ExportContext } from '../src/ExportContext';
import { PdfExportStrategy } from '../src/strategies/PdfExportStrategy';
import { ExcelExportStrategy } from '../src/strategies/ExcelExportStrategy';
import { FinancialReport } from '../src/models/FinancialReport';

describe('Export Strategy Pattern', () => {
    const report = new FinancialReport('TestCompany', 2027, 1000000);

    it('should export to real PDF', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        const result = await context.executeExport(report);
        
        // Проверяем, что это реальный PDF (начинается с %PDF)
        expect(result.subarray(0, 4).toString()).toBe('%PDF');
    });

    it('should switch to real Excel export', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        context.setStrategy(new ExcelExportStrategy());
        const result = await context.executeExport(report);
        
        // Проверяем, что это реальный Excel (ZIP-архив, начинается с PK)
        expect(result.subarray(0, 2).toString()).toBe('PK');
    });
});