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

    public async executeExport(report: FinancialReport): Promise<Blob> {
        return this.strategy.execute(report);
    }
}