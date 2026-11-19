# Finance Forecast System — demo website

Python / Flask UI prototype based on the supplied brief. Sample values are illustrative, not actual company/model outputs.

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then visit http://127.0.0.1:5000

## Included
- Role switcher (Analyst / Risk manager / Administrator / Investor)
- Company search by name, INN, ticker, sector; demo company listing
- Forecast dashboard with demo chart and simulated POST endpoint
- Risk analysis screen with MAE/RMSE/MAPE illustrative metrics
- Admin user list, file-upload interaction mock, model retraining mock
- Investor feed adapted for mobile-width screens, favorite and compare demo actions
- Flask JSON endpoints: `/api/companies`, `/api/forecast`, `/api/users`, `/api/admin/upload`, `/api/admin/retrain`

This is a functional UI prototype. It does not connect to actual financial feeds, databases, trained ML models or auth; forecast and exports are simulated.
