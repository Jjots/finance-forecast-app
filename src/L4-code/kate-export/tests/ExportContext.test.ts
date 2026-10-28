import { ExportContext } from '../src/ExportContext';
import { PdfExportStrategy } from '../src/strategies/PdfExportStrategy';
import { ExcelExportStrategy } from '../src/strategies/ExcelExportStrategy';
import { FinancialReport } from '../src/models/FinancialReport';

describe('Export Strategy Pattern', () => {
    const report = new FinancialReport('TestCompany', 2027, 1000000);

    it('should export to Blob PDF', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        const result = await context.executeExport(report);
        
        expect(result).toBeInstanceOf(Blob);
        expect(result.type).toBe('application/pdf');
    });

    it('should switch to Blob Excel export', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        context.setStrategy(new ExcelExportStrategy());
        const result = await context.executeExport(report);
        
        expect(result).toBeInstanceOf(Blob);
        expect(result.type).toBe('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    });
});