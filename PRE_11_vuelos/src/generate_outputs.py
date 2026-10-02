from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"

COUNTS = [
    "scheduled_flights",
    "cancelled_flights",
    "operated_flights",
    "delayed_departure_15_flights",
    "positive_departure_delay_minutes",
]


def add_rates(frame: pd.DataFrame) -> pd.DataFrame:
    frame["cancellation_rate"] = frame["cancelled_flights"] / frame["scheduled_flights"]
    frame["delay_15_rate"] = frame["delayed_departure_15_flights"] / frame["operated_flights"]
    frame["avg_delay_minutes"] = (
        frame["positive_departure_delay_minutes"] / frame["operated_flights"]
    )
    return frame.round(4)


def summarize(flights: pd.DataFrame, keys) -> pd.DataFrame:
    return add_rates(flights.groupby(keys, as_index=False)[COUNTS].sum())


def generate_outputs() -> None:
    monthly = pd.read_csv(DATA_DIRECTORY / "flights_by_carrier_month.csv.gz")
    day_hour = pd.read_csv(DATA_DIRECTORY / "flights_by_carrier_day_hour.csv.gz")

    overall = add_rates(monthly[COUNTS].sum().to_frame().T)
    overall.insert(0, "carriers", monthly["reporting_airline"].nunique())

    # Segments with too few flights give noisy rates.
    segments = summarize(
        day_hour, ["reporting_airline", "day_of_week", "scheduled_departure_hour"]
    )
    segments = segments[segments["operated_flights"] >= 1000]

    outputs = {
        "overall_kpis": overall,
        "carrier_summary": summarize(monthly, "reporting_airline").sort_values(
            "delay_15_rate", ascending=False
        ),
        "monthly_national_kpis": summarize(monthly, ["year", "month"]),
        "seasonality": summarize(monthly, "month"),
        "day_hour_delay": summarize(day_hour, ["day_of_week", "scheduled_departure_hour"]),
        "priority_segments": segments.sort_values(
            "delayed_departure_15_flights", ascending=False
        ).head(20),
    }

    SUBMISSION_DIRECTORY.mkdir(exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(SUBMISSION_DIRECTORY / f"{name}.csv", index=False)


if __name__ == "__main__":
    generate_outputs()
