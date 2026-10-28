import { ExportStrategy } from './strategies/ExportStrategy';
import { FinancialReport } from './models/FinancialReport';

export class ExportContext {
    private strategy: ExportStrategy;

    constructor(strategy: ExportStrategy) {
        this.strategy = strategy;
    }

    public setStrategy(strategy: ExportStrategy): void {
        this.strategy = strategy;
    }

    // Переименовали executeExport в export (как в ТЗ)
    public async export(report: FinancialReport): Promise<Blob> {
        return this.strategy.execute(report);
    }
}