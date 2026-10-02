from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"


def generate_outputs() -> None:
    drivers = pd.read_csv(DATA_DIRECTORY / "drivers.csv")
    timesheet = pd.read_csv(DATA_DIRECTORY / "timesheet.csv")

    summary = (
        timesheet.groupby("driverId", as_index=False)
        .agg(
            total_hours=("hours-logged", "sum"),
            total_miles=("miles-logged", "sum"),
            weeks_logged=("week", "nunique"),
        )
        .merge(drivers[["driverId", "name"]], on="driverId", how="left")
        [["driverId", "name", "total_hours", "total_miles", "weeks_logged"]]
        .sort_values("total_miles", ascending=False)
    )

    SUBMISSION_DIRECTORY.mkdir(exist_ok=True)
    summary.to_csv(SUBMISSION_DIRECTORY / "summary.csv", index=False)

    top10 = summary.head(10).sort_values("total_miles")
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.barh(top10["name"], top10["total_miles"], color="#2f6f9f")
    axis.set_title("Top 10 drivers by miles logged")
    axis.set_xlabel("Miles logged")
    axis.set_ylabel("Driver")
    figure.tight_layout()
    figure.savefig(SUBMISSION_DIRECTORY / "top10_drivers.png", dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    generate_outputs()