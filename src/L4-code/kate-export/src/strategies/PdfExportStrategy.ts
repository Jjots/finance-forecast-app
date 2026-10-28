import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';

export class PdfExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Buffer> {
        console.log(`[PDF Export] Generating PDF for ${report.company}`);
        return Buffer.from('PDF_STUB_CONTENT');
    }
}