import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';
import ExcelJS from 'exceljs';

export class ExcelExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Buffer> {
        console.log(`[Excel Export] Generating real Excel for ${report.company}`);
        
        const workbook = new ExcelJS.Workbook();
        const worksheet = workbook.addWorksheet('Forecast');

        worksheet.columns = [
            { header: 'Company', key: 'company', width: 25 },
            { header: 'Forecast Year', key: 'forecastYear', width: 15 },
            { header: 'Revenue Forecast (RUB)', key: 'revenueForecast', width: 20 }
        ];

        worksheet.addRow({
            company: report.company,
            forecastYear: report.forecastYear,
            revenueForecast: report.revenueForecast
        });

        // Сохраняем реальный файл на диск для демонстрации
        await workbook.xlsx.writeFile('report.xlsx');

        const buffer = await workbook.xlsx.writeBuffer();
        return Buffer.from(buffer);
    }
}