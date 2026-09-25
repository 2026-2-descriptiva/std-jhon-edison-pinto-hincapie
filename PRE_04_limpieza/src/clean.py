import re
import unicodedata
from pathlib import Path

import pandas as pd


def _supplier_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]", "", normalized.casefold())


def _supplier_name(value: str) -> str:
    value = re.sub(r"\s+", " ", str(value).strip())
    value = re.sub(r"\bS\.?\s*A\.?\s*S?\.?\b", "S.A.S.", value, flags=re.I)
    value = re.sub(r"\bS\.?\s*A\.?\b", "S.A.", value, flags=re.I)
    value = re.sub(r"\bLTDA\.?\b", "Ltda.", value, flags=re.I)
    value = value.title()
    return re.sub(r"\b(Ibm|Sap|Aws)\b", lambda match: match.group().upper(), value)


def main():
    folder = Path(__file__).resolve().parents[1]
    source = folder / "data" / "ventas.csv"
    destination = folder / "submission" / "ventas.csv"

    dataframe = pd.read_csv(source, dtype=str)
    dataframe.columns = [column.strip().lower() for column in dataframe.columns]

    suppliers = {}
    for value in dataframe["supplier"].fillna(""):
        key = _supplier_key(value)
        if key and key not in suppliers:
            suppliers[key] = _supplier_name(value)
    dataframe["supplier"] = dataframe["supplier"].map(
        lambda value: suppliers.get(_supplier_key(value), value)
    )

    dataframe["country"] = (
        dataframe["country"].str.strip().str.upper().replace({"COLOMBIA": "COL", "CO": "COL"})
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(destination, index=False)
