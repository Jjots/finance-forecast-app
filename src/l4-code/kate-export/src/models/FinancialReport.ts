export class FinancialReport {
    constructor(
        public readonly company: string,
        public readonly forecastYear: number,
        public readonly revenueForecast: number
    ) {}
}
