import { FinancialReport } from '../models/FinancialReport';

export interface ExportStrategy {
    execute(report: FinancialReport): Promise<Blob>;
}