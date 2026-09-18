import csv
import json
from pathlib import Path


def convert_csv_2_json(csv_file):
    csv_path = Path(csv_file)
    output_path = csv_path.parent.parent / "temp" / f"{csv_path.stem}.json"

    with csv_path.open(newline="", encoding="utf-8") as file:
        data = list(csv.DictReader(file))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
