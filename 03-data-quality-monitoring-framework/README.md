# 03 — Data Quality Monitoring Framework
Configuration-driven checks for required columns, nulls, uniqueness, accepted values and numeric thresholds. Emits JSON quality report and a CI-friendly exit code.

Run:
```bash
pip install -r requirements.txt
python run_quality.py --data-dir ../datasets --report-dir reports
pytest -q
```
Add or change rules in `config/rules.json`; no engine code changes are needed for supported rule types.
