import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"

SUMMARY_QUERY = """
SELECT
    t.driverId,
    d.name,
    SUM(t."hours-logged") AS total_hours,
    SUM(t."miles-logged") AS total_miles,
    COUNT(DISTINCT t.week) AS weeks_logged
FROM timesheet AS t
LEFT JOIN drivers AS d ON d.driverId = t.driverId
GROUP BY t.driverId, d.name
ORDER BY total_miles DESC
"""


def generate_outputs() -> None:
    with sqlite3.connect(":memory:") as connection:
        for table in ("drivers", "timesheet"):
            pd.read_csv(DATA_DIRECTORY / f"{table}.csv").to_sql(
                table, connection, index=False
            )
        summary = pd.read_sql_query(SUMMARY_QUERY, connection)

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
