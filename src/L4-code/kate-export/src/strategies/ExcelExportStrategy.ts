import { ExportStrategy } from './ExportStrategy';
import { FinancialReport } from '../models/FinancialReport';
import * as XLSX from 'xlsx';

export class ExcelExportStrategy implements ExportStrategy {
    public async execute(report: FinancialReport): Promise<Blob> {
        console.log(`[Excel Export] Generating Blob Excel for ${report.company}`);
        
        const data = [{
            Company: report.company,
            ForecastYear: report.forecastYear,
            RevenueForecast: report.revenueForecast
        }];

        const worksheet = XLSX.utils.json_to_sheet(data);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Forecast');

        // Генерируем массив байтов (ArrayBuffer)
        const arrayBuffer = XLSX.write(workbook, { type: 'array', bookType: 'xlsx' });
        
        // Оборачиваем в Blob (как в браузере)
        return new Blob([arrayBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    }
}