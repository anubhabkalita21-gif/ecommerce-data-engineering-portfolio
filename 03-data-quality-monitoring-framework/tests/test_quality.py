import json
import pandas as pd

from src.quality import validate, run


def test_unique_fails_on_duplicates():
    result = validate(
        pd.DataFrame({"id": [1, 1]}),
        [{"name": "unique", "type": "unique", "column": "id"}]
    )
    assert result["status"] == "FAIL"


def test_accepted_values_pass():
    result = validate(
        pd.DataFrame({"status": ["paid"]}),
        [{
            "name": "status",
            "type": "accepted_values",
            "column": "status",
            "values": ["paid", "refunded"]
        }]
    )
    assert result["status"] == "PASS"


def test_required_columns_fail():
    result = validate(
        pd.DataFrame({"id": [1]}),
        [{
            "name": "required",
            "type": "required_columns",
            "columns": ["id", "email"]
        }]
    )
    assert result["status"] == "FAIL"


def test_not_null_fails():
    result = validate(
        pd.DataFrame({"email": ["a@test.com", None]}),
        [{"name": "email", "type": "not_null", "column": "email"}]
    )
    assert result["failed_checks"] == 1


def test_greater_than_fails():
    result = validate(
        pd.DataFrame({"quantity": [5, 0, -1]}),
        [{
            "name": "quantity",
            "type": "greater_than",
            "column": "quantity",
            "value": 0
        }]
    )
    assert result["results"][0]["failed_records"] == 2


def test_greater_equal_passes():
    result = validate(
        pd.DataFrame({"price": [0, 10, 20]}),
        [{
            "name": "price",
            "type": "greater_equal",
            "column": "price",
            "value": 0
        }]
    )
    assert result["status"] == "PASS"


def test_quality_report_is_created(tmp_path):
    data = tmp_path / "data"
    data.mkdir()

    pd.DataFrame({"id": [1, 2]}).to_csv(
        data / "sample.csv", index=False
    )

    config = tmp_path / "rules.json"
    config.write_text(json.dumps({
        "sample": [{
            "name": "unique",
            "type": "unique",
            "column": "id"
        }]
    }))

    report_dir = tmp_path / "reports"

    result = run(data, config, report_dir)

    assert result["overall_status"] == "PASS"
    assert (report_dir / "quality_report.json").exists()
    assert (report_dir / "quality_report.html").exists()
        


def test_missing_dataset_fails(tmp_path):
    config = tmp_path / "rules.json"
    config.write_text(json.dumps({"missing": []}))

    result = run(
        tmp_path / "data",
        config,
        tmp_path / "reports"
    )

    assert result["overall_status"] == "FAIL"