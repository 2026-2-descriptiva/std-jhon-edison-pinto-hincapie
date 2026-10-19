from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"


def summarize(campaigns: pd.DataFrame, keys) -> pd.DataFrame:
    return (
        campaigns.groupby(keys, as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            page_clicks=("page_clicks", "sum"),
            paid_clicks=("paid_clicks", "sum"),
            blocked_clicks=("blocked_clicks", "sum"),
            ad_spend=("ad_spend", "sum"),
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .assign(
            ctr=lambda frame: frame["page_clicks"] / frame["impressions"],
            roas=lambda frame: frame["revenue"] / frame["ad_spend"],
            cpc=lambda frame: frame["ad_spend"] / frame["paid_clicks"],
            rpc=lambda frame: frame["revenue"] / frame["page_clicks"],
        )
        .round(4)
    )


def generate_outputs() -> None:
    campaigns = pd.read_csv(DATA_DIRECTORY / "campaign_data.csv", parse_dates=["utc_date"])

    kpis = summarize(campaigns.assign(scope="total"), "scope").drop(columns="scope")
    kpis.insert(0, "rows", len(campaigns))

    outputs = {
        "kpis": kpis,
        "source_summary": summarize(campaigns, "traffic_source").sort_values(
            "gross_profit", ascending=False
        ),
        "campaign_summary": summarize(campaigns, ["template_name", "campaign_url"]).sort_values(
            "gross_profit", ascending=False
        ),
        "daily_summary": summarize(campaigns, "utc_date").sort_values("utc_date"),
    }

    SUBMISSION_DIRECTORY.mkdir(exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(SUBMISSION_DIRECTORY / f"{name}.csv", index=False)


if __name__ == "__main__":
    generate_outputs()
