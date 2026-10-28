import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';

export class ExcelExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Buffer> {
        console.log(`[Excel Export] Generating Excel for ${report.company}`);
        return Buffer.from('EXCEL_STUB_CONTENT');
    }
}