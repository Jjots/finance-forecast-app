import { ExportContext } from '../src/ExportContext';
import { PdfExportStrategy } from '../src/strategies/PdfExportStrategy';
import { ExcelExportStrategy } from '../src/strategies/ExcelExportStrategy';
import { FinancialReport } from '../src/models/FinancialReport';

describe('Export Strategy Pattern', () => {
    const validReport = new FinancialReport('TestCompany', 2027, 1000000);
    const invalidReport = new FinancialReport('', 1999, -100);

    // --- ПОЛОЖИТЕЛЬНЫЕ ТЕСТЫ ---

    it('should export to real PDF (check signature)', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        const blob = await context.export(validReport);
        
        expect(blob).toBeInstanceOf(Blob);
        expect(blob.type).toBe('application/pdf');

        const buffer = await blob.arrayBuffer();
        const firstBytes = new Uint8Array(buffer.slice(0, 4));
        expect(String.fromCharCode(...firstBytes)).toBe('%PDF');
    });

    it('should switch to real Excel (check signature)', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        context.setStrategy(new ExcelExportStrategy());
        const blob = await context.export(validReport);
        
        expect(blob).toBeInstanceOf(Blob);
        expect(blob.type).toBe('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');

        const buffer = await blob.arrayBuffer();
        const firstBytes = new Uint8Array(buffer.slice(0, 2));
        expect(String.fromCharCode(...firstBytes)).toBe('PK');
    });

    // --- ОТРИЦАТЕЛЬНЫЕ ТЕСТЫ ---

    it('should throw error for invalid PDF report', async () => {
        const context = new ExportContext(new PdfExportStrategy());
        await expect(context.export(invalidReport)).rejects.toThrow('Не удалось сгенерировать PDF');
    });

    it('should throw error for invalid Excel report', async () => {
        const context = new ExportContext(new ExcelExportStrategy());
        await expect(context.export(invalidReport)).rejects.toThrow('Не удалось сгенерировать Excel');
    });
});