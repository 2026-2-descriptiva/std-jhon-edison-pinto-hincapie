from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"


def summarize(shipments: pd.DataFrame, keys) -> pd.DataFrame:
    return (
        shipments.groupby(keys, as_index=False)
        .agg(
            shipments=("ID", "count"),
            units=("Line Item Quantity", "sum"),
            value_usd=("Line Item Value", "sum"),
            weight_kg=("Weight", "sum"),
            freight_usd=("Freight", "sum"),
            late_rate=("Late", "mean"),
            avg_delay_days=("DelayDays", "mean"),
        )
        .assign(freight_per_kg=lambda frame: frame["freight_usd"] / frame["weight_kg"])
        .round(4)
    )


def generate_outputs() -> None:
    shipments = pd.read_csv(DATA_DIRECTORY / "supply_chain.csv")

    # Weight and freight hold text notes ("See ASN-93", "Freight Included...").
    shipments["Weight"] = pd.to_numeric(shipments["Weight (Kilograms)"], errors="coerce")
    shipments["Freight"] = pd.to_numeric(shipments["Freight Cost (USD)"], errors="coerce")

    for column in ["Scheduled Delivery Date", "Delivered to Client Date"]:
        shipments[column] = pd.to_datetime(shipments[column], format="%d-%b-%y", errors="coerce")
    shipments["Month"] = shipments["Delivered to Client Date"].dt.to_period("M").astype(str)
    shipments["DelayDays"] = (
        shipments["Delivered to Client Date"] - shipments["Scheduled Delivery Date"]
    ).dt.days
    shipments["Late"] = (shipments["DelayDays"] > 0).astype(int)

    # Freight stats only make sense where freight and weight were captured.
    freight_known = shipments.dropna(subset=["Weight", "Freight"])
    modes = shipments.dropna(subset=["Shipment Mode"])

    overall = pd.DataFrame(
        {
            "shipments": [len(shipments)],
            "countries": [shipments["Country"].nunique()],
            "units": [shipments["Line Item Quantity"].sum()],
            "value_usd": [shipments["Line Item Value"].sum()],
            "freight_usd": [shipments["Freight"].sum()],
            "late_rate": [shipments["Late"].mean()],
            "avg_delay_days": [shipments["DelayDays"].mean()],
        }
    ).round(4)

    country_mode = summarize(modes, ["Country", "Shipment Mode"])
    # Segments with few shipments give noisy rates.
    segments = country_mode[country_mode["shipments"] >= 30]
    countries = summarize(shipments, "Country")

    outputs = {
        "overall_kpis": overall,
        "country_summary": countries.sort_values("value_usd", ascending=False),
        "mode_summary": summarize(modes, "Shipment Mode").sort_values(
            "value_usd", ascending=False
        ),
        "country_mode_summary": country_mode.sort_values(["Country", "Shipment Mode"]),
        "monthly_summary": summarize(shipments.dropna(subset=["Month"]), "Month")
        .query("Month != 'NaT'")
        .sort_values("Month"),
        "freight_by_mode": summarize(freight_known.dropna(subset=["Shipment Mode"]), "Shipment Mode")
        .sort_values("freight_per_kg", ascending=False),
        "priority_countries": countries.sort_values("late_rate", ascending=False)
        .query("shipments >= 30")
        .head(10),
        "priority_segments": segments.sort_values("late_rate", ascending=False).head(20),
    }

    SUBMISSION_DIRECTORY.mkdir(exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(SUBMISSION_DIRECTORY / f"{name}.csv", index=False)


if __name__ == "__main__":
    generate_outputs()
