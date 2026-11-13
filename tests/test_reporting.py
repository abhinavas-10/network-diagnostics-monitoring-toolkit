import csv
import json
from network_toolkit.reporting import export_csv, export_json

def test_export_json(tmp_path):
    records = [{"target": "localhost", "success": True}]
    output = tmp_path / "reports" / "result.json"
    export_json(records, str(output))
    assert json.loads(output.read_text()) == records

def test_export_csv(tmp_path):
    records = [{"target": "localhost", "success": True}]
    output = tmp_path / "result.csv"
    export_csv(records, str(output))
    with output.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["target"] == "localhost"
