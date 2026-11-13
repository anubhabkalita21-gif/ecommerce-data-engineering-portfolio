import json
from pathlib import Path
from datetime import datetime, timezone
from html import escape

import pandas as pd


def check(df, rule):
    rule_type = rule["type"]
    name = rule["name"]
    column = rule.get("column")

    if rule_type == "required_columns":
        missing = sorted(set(rule["columns"]) - set(df.columns))
        failures = max(1, len(missing)) if missing else 0
        detail = (
            f"Missing columns: {missing}"
            if missing else "All columns present"
        )

    elif column not in df.columns:
        failures = max(1, len(df))
        detail = f"Missing column: {column}"

    elif rule_type == "not_null":
        failures = int(df[column].isna().sum())
        detail = f"{failures} null values"

    elif rule_type == "unique":
        failures = int(df[column].duplicated(keep=False).sum())
        detail = f"{failures} duplicate rows"

    elif rule_type == "accepted_values":
        invalid = (
            ~df[column].isin(rule["values"])
            & df[column].notna()
        )
        failures = int(invalid.sum())
        detail = f"{failures} invalid values"

    elif rule_type in ("greater_than", "greater_equal"):
        values = pd.to_numeric(df[column], errors="coerce")

        if rule_type == "greater_than":
            invalid = values.isna() | (values <= rule["value"])
        else:
            invalid = values.isna() | (values < rule["value"])

        failures = int(invalid.sum())
        detail = f"{failures} threshold violations"

    else:
        raise ValueError(f"Unknown rule type: {rule_type}")

    return {
        "rule": name,
        "passed": failures == 0,
        "failed_records": failures,
        "detail": detail
    }


def validate(df, rules):
    results = [check(df, rule) for rule in rules]

    passed = sum(result["passed"] for result in results)
    failed = len(results) - passed
    total = len(results)

    return {
        "row_count": len(df),
        "check_count": total,
        "passed_checks": passed,
        "failed_checks": failed,
        "pass_rate": round(
            passed / total * 100, 2
        ) if total else 100.0,
        "status": "PASS" if failed == 0 else "FAIL",
        "results": results
    }


def write_html_report(report, output_path):
    summary = report["summary"]
    rows = []

    for dataset, details in report["datasets"].items():
        for result in details["results"]:
            status = "PASS" if result["passed"] else "FAIL"

            rows.append(
                f"<tr>"
                f"<td>{escape(dataset)}</td>"
                f"<td>{escape(result['rule'])}</td>"
                f"<td class='{status}'>{status}</td>"
                f"<td>{result['failed_records']}</td>"
                f"<td>{escape(result['detail'])}</td>"
                f"</tr>"
            )

    table_rows = "\n".join(rows)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>Data Quality Dashboard</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f3f4f6;
                color: #1f2937;
                padding: 30px;
                margin: 0;
            }}

            .container {{
                max-width: 1100px;
                margin: auto;
            }}

            .cards {{
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(180px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px #0001;
            }}

            .value {{
                font-size: 28px;
                font-weight: bold;
                margin-top: 10px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th, td {{
                padding: 13px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}

            th {{
                background: #1f2937;
                color: white;
            }}

            .PASS {{
                color: #15803d;
                font-weight: bold;
            }}

            .FAIL {{
                color: #dc2626;
                font-weight: bold;
            }}

            .table-wrap {{
                overflow-x: auto;
            }}

            .status {{
                padding: 12px;
                border-radius: 8px;
                background: white;
                display: inline-block;
                font-weight: bold;
            }}
        </style>
    </head>

    <body>
        <div class="container">

            <h1>Data Quality Dashboard</h1>

            <p>
                Generated:
                {escape(report["generated_at_utc"])}
            </p>

            <div class="status {report["overall_status"]}">
                Overall Status: {report["overall_status"]}
            </div>

            <div class="cards">

                <div class="card">
                    Datasets
                    <div class="value">
                        {summary["dataset_count"]}
                    </div>
                </div>

                <div class="card">
                    Total Rows
                    <div class="value">
                        {summary["total_rows"]}
                    </div>
                </div>

                <div class="card">
                    Passed Checks
                    <div class="value">
                        {summary["passed_checks"]}
                    </div>
                </div>

                <div class="card">
                    Failed Checks
                    <div class="value">
                        {summary["failed_checks"]}
                    </div>
                </div>

                <div class="card">
                    Pass Rate
                    <div class="value">
                        {summary["pass_rate"]}%
                    </div>
                </div>

            </div>

            <h2>Validation Results</h2>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Dataset</th>
                            <th>Rule</th>
                            <th>Status</th>
                            <th>Failed Records</th>
                            <th>Details</th>
                        </tr>
                    </thead>

                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>

        </div>
    </body>
    </html>
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        html_content,
        encoding="utf-8"
    )


def run(data_dir, config, report_dir):
    data_path = Path(data_dir)

    config_data = json.loads(
        Path(config).read_text(encoding="utf-8")
    )

    report_path = Path(report_dir)
    report_path.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {"datasets": {}}

    # Validate every configured dataset
    for name, rules in config_data.items():

        file_path = data_path / f"{name}.csv"

        if file_path.exists():
            df = pd.read_csv(file_path)

            output["datasets"][name] = validate(
                df,
                rules
            )

        else:
            output["datasets"][name] = {
                "row_count": 0,
                "check_count": 1,
                "passed_checks": 0,
                "failed_checks": 1,
                "pass_rate": 0.0,
                "status": "FAIL",
                "results": [{
                    "rule": "file_exists",
                    "passed": False,
                    "failed_records": 1,
                    "detail": f"Missing dataset: {file_path}"
                }]
            }

    # Calculate overall metrics
    datasets = list(output["datasets"].values())

    total_checks = sum(
        dataset["check_count"] for dataset in datasets
    )

    passed_checks = sum(
        dataset["passed_checks"] for dataset in datasets
    )

    failed_checks = sum(
        dataset["failed_checks"] for dataset in datasets
    )

    passed_datasets = sum(
        dataset["status"] == "PASS"
        for dataset in datasets
    )

    failed_datasets = len(datasets) - passed_datasets

    summary = {
        "dataset_count": len(datasets),
        "passed_datasets": passed_datasets,
        "failed_datasets": failed_datasets,
        "total_rows": sum(
            dataset["row_count"] for dataset in datasets
        ),
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "pass_rate": round(
            passed_checks / total_checks * 100, 2
        ) if total_checks else 100.0
    }

    output["generated_at_utc"] = (
        datetime.now(timezone.utc).isoformat()
    )

    output["overall_status"] = (
        "PASS" if failed_checks == 0 else "FAIL"
    )

    output["summary"] = summary

    # Generate JSON report
    (report_path / "quality_report.json").write_text(
        json.dumps(output, indent=2),
        encoding="utf-8"
    )

    # Generate HTML dashboard
    write_html_report(
        output,
        report_path / "quality_report.html"
    )

    return output