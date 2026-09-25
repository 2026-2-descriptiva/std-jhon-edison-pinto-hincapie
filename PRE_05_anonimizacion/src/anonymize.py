import csv
from pathlib import Path


INPUT_FILE = Path(__file__).parents[1] / "data" / "raw.csv"
OUTPUT_FILE = Path(__file__).parents[1] / "submission" / "anonymized.csv"


def anonymize(input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with input_file.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        rows = []
        for row_id, row in enumerate(reader, start=1):
            row["name"] = f"person_{row_id:04d}"
            row["document_id"] = f"document_{row_id:04d}"
            row["email"] = f"user_{row_id:04d}@example.invalid"
            row["loyalty_card_number"] = f"card_{row_id:04d}"
            rows.append(row)

    with output_file.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    anonymize()