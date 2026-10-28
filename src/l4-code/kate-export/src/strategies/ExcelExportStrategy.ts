import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';
import * as XLSX from 'xlsx';

export class ExcelExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Blob> {
        try {
            if (!report.company || report.forecastYear < 2000 || report.revenueForecast < 0) {
                throw new Error('Некорректные данные для генерации Excel');
            }

            console.log(`[Excel Export] Generating Blob Excel for ${report.company}`);
            const data = [{
                Company: report.company,
                ForecastYear: report.forecastYear,
                RevenueForecast: report.revenueForecast
            }];
            const worksheet = XLSX.utils.json_to_sheet(data);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, 'Forecast');
            
            const arrayBuffer = XLSX.write(workbook, { type: 'array', bookType: 'xlsx' });
            return new Blob([arrayBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        } catch (error) {
            console.error('Ошибка при генерации Excel:', error);
            throw new Error('Не удалось сгенерировать Excel');
        }
    }
}