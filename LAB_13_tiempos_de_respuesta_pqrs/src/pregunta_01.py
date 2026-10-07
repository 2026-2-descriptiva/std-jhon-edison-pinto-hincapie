from pathlib import Path

import numpy as np
import pandas as pd

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _load(channel: str) -> pd.DataFrame:
    df = pd.read_csv(
        f"data/historical_requests_{channel}.csv.gz",
        parse_dates=["in_date", "out_date"],
    ).drop_duplicates()
    df["channel"] = channel

    answered = df["out_date"].notna()
    start = df["in_date"].values.astype("datetime64[D]") + 1
    # pending rows: use in_date as a placeholder, masked to NaN below
    end = df["out_date"].fillna(df["in_date"]).values.astype("datetime64[D]") + 1
    business = np.busday_count(start, end).astype(float)
    df["business_days"] = np.where(answered, business, np.nan)
    df["calendar_days"] = (df["out_date"] - df["in_date"]).dt.days
    df["on_time"] = df["business_days"] <= 15  # NaN (pending) -> False
    df["year"] = df["in_date"].dt.year
    return df


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Mide el cumplimiento del plazo legal de 15 días hábiles en PQRS.

    Genera en `submission/` channel_summary.csv, yearly_summary.csv y
    entry_day_summary.csv, y retorna las tres tablas en ese orden.
    """
    df = pd.concat([_load("letter"), _load("web")], ignore_index=True)
    df["pending"] = df["out_date"].isna()

    channels = (
        df.groupby("channel")
        .agg(
            requests=("channel", "size"),
            pending=("pending", "sum"),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
    )
    channels["answered"] = channels["requests"] - channels["pending"]
    channels = channels[
        [
            "channel",
            "requests",
            "answered",
            "pending",
            "median_business_days",
            "on_time_rate",
        ]
    ].round({"on_time_rate": 4})

    yearly = (
        df.groupby(["year", "channel"])
        .agg(
            requests=("channel", "size"),
            pending=("pending", "sum"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .round({"on_time_rate": 4})
    )

    entry_days = (
        df.groupby("day_name")
        .agg(
            requests=("day_name", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .reindex(DAYS)
        .reset_index()
    )

    out = Path("submission")
    out.mkdir(exist_ok=True)
    channels.to_csv(out / "channel_summary.csv", index=False)
    yearly.to_csv(out / "yearly_summary.csv", index=False)
    entry_days.to_csv(out / "entry_day_summary.csv", index=False)

    return channels, yearly, entry_days
