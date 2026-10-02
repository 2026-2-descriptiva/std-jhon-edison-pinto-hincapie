from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"


def summarize(sales: pd.DataFrame, keys) -> pd.DataFrame:
    return (
        sales.groupby(keys, as_index=False)
        .agg(
            orders=("OrderID", "count"),
            units=("Quantity", "sum"),
            revenue=("TotalAmount", "sum"),
            net_revenue=("NetAmount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .round(4)
        .sort_values("revenue", ascending=False)
    )


def generate_outputs() -> None:
    sales = pd.read_csv(DATA_DIRECTORY / "sales.csv", parse_dates=["OrderDate"])
    sales["NetAmount"] = sales["TotalAmount"] * (1 - sales["IsReturned"])
    sales["Month"] = sales["OrderDate"].dt.to_period("M").astype(str)
    sales["DayType"] = sales["OrderDate"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )

    kpis = pd.DataFrame(
        {
            "orders": [len(sales)],
            "customers": [sales["CustomerID"].nunique()],
            "units": [sales["Quantity"].sum()],
            "revenue": [sales["TotalAmount"].sum()],
            "net_revenue": [sales["NetAmount"].sum()],
            "avg_order_value": [sales["TotalAmount"].mean()],
            "return_rate": [sales["IsReturned"].mean()],
        }
    ).round(4)

    segments = summarize(sales, ["Category", "SalesChannel"])

    outputs = {
        "kpi_summary": kpis,
        "monthly_sales": summarize(sales, "Month").sort_values("Month"),
        "category_summary": summarize(sales, "Category"),
        "payment_summary": summarize(sales, "PaymentMethod"),
        "day_type_summary": summarize(sales, "DayType"),
        "top_customers": summarize(sales, "CustomerID").head(10),
        "top_products": summarize(sales, ["ProductID", "ProductName", "Category"]).head(10),
        "return_risk": segments.sort_values("return_rate", ascending=False),
        "priority_segments": segments.sort_values("net_revenue", ascending=False),
    }

    SUBMISSION_DIRECTORY.mkdir(exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(SUBMISSION_DIRECTORY / f"{name}.csv", index=False)


if __name__ == "__main__":
    generate_outputs()
