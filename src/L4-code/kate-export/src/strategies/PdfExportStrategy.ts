import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';
import PDFDocument from 'pdfkit';
import * as fs from 'fs';

export class PdfExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Buffer> {
        console.log(`[PDF Export] Generating real PDF for ${report.company}`);
        
        return new Promise((resolve, reject) => {
            const doc = new PDFDocument();
            const buffers: Buffer[] = [];

            doc.on('data', buffers.push.bind(buffers));
            doc.on('end', () => {
                const pdfData = Buffer.concat(buffers);
                
                // Сохраняем реальный файл на диск для демонстрации
                fs.writeFileSync('report.pdf', pdfData);
                
                resolve(pdfData);
            });
            doc.on('error', reject);

            doc.fontSize(20).text('Financial Forecast Report', { align: 'center' });
            doc.moveDown();
            doc.fontSize(14).text(`Company: ${report.company}`);
            doc.text(`Forecast Year: ${report.forecastYear}`);
            doc.text(`Revenue Forecast: ${report.revenueForecast} RUB`);
            
            doc.end();
        });
    }
}