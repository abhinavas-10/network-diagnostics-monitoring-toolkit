"""CSV and JSON report exporters."""
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

def export_json(records: Iterable[Dict[str, Any]], output: str) -> str:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(list(records), handle, indent=2, ensure_ascii=False)
    return str(path)

def export_csv(records: Iterable[Dict[str, Any]], output: str) -> str:
    rows = list(records)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    if not fields:
        fields = ["timestamp", "operation", "target", "success", "error"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return str(path)
