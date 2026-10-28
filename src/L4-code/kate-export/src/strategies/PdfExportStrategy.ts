import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';
import { jsPDF } from 'jspdf';

export class PdfExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Blob> {
        try {
            console.log(`[PDF Export] Generating Blob PDF for ${report.company}`);
            const doc = new jsPDF();
            doc.text('Financial Forecast Report', 10, 10);
            doc.text(`Company: ${report.company}`, 10, 20);
            doc.text(`Forecast Year: ${report.forecastYear}`, 10, 30);
            doc.text(`Revenue Forecast: ${report.revenueForecast} RUB`, 10, 40);
            return doc.output('blob');
        } catch (error) {
            console.error('Ошибка при генерации PDF:', error);
            throw new Error('Не удалось сгенерировать PDF');
        }
    }
}