from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
SUBMISSION_DIRECTORY = PROJECT_ROOT / "submission"

SALARY = "salario_mensual_cop"
HIGH_SALARY_QUANTILE = 0.9
# Pay below this share of the peer median is flagged for review.
FLOOR_RATIO = 0.85


def generate_outputs() -> None:
    salaries = pd.read_csv(DATA_DIRECTORY / "salarios.csv")
    company_median = salaries[SALARY].median()

    department_pay_gap = (
        salaries.groupby(["gerencia", "departamento"], as_index=False)
        .agg(
            employees=("employee_id", "count"),
            avg_experience_years=("experiencia_tecnica_anios", "mean"),
            avg_salary=(SALARY, "mean"),
            median_salary=(SALARY, "median"),
        )
        .assign(gap_vs_company_median=lambda frame: frame["median_salary"] / company_median - 1)
        .sort_values("gap_vs_company_median")
        .round(4)
    )

    high_threshold = salaries[SALARY].quantile(HIGH_SALARY_QUANTILE)
    salaries["high_salary"] = salaries[SALARY] >= high_threshold
    high_salary_by_career = (
        salaries.groupby(["trayectoria", "categoria"], as_index=False)
        .agg(employees=("employee_id", "count"), high_earners=("high_salary", "sum"))
        .assign(high_share=lambda frame: frame["high_earners"] / frame["employees"])
        .assign(high_salary_threshold=round(high_threshold, 2))
        .sort_values("high_share", ascending=False)
        .round(4)
    )

    peer_median = salaries.groupby(["trayectoria", "categoria"])[SALARY].transform("median")
    salaries["peer_median"] = peer_median
    salaries["ratio_to_peer"] = salaries[SALARY] / peer_median
    below_floor = salaries[salaries["ratio_to_peer"] < FLOOR_RATIO]
    recommendations = (
        below_floor.assign(
            recommended_salary=lambda frame: (frame["peer_median"] * FLOOR_RATIO).round(0),
            recommended_increase=lambda frame: frame["recommended_salary"] - frame[SALARY],
        )[
            [
                "employee_id",
                "gerencia",
                "departamento",
                "trayectoria",
                "categoria",
                "experiencia_tecnica_anios",
                SALARY,
                "peer_median",
                "ratio_to_peer",
                "recommended_salary",
                "recommended_increase",
            ]
        ]
        .sort_values("ratio_to_peer")
        .round(4)
    )

    top, bottom = department_pay_gap.iloc[-1], department_pay_gap.iloc[0]
    by_path = salaries.groupby("trayectoria")[SALARY].median()
    conclusions = pd.DataFrame(
        [
            ("employees", len(salaries)),
            ("company_median_salary", company_median),
            ("high_salary_threshold_p90", high_threshold),
            ("highest_paid_department", top["departamento"]),
            ("highest_department_gap_vs_median", top["gap_vs_company_median"]),
            ("lowest_paid_department", bottom["departamento"]),
            ("lowest_department_gap_vs_median", bottom["gap_vs_company_median"]),
            ("directiva_vs_tecnica_median_ratio", by_path["Directiva"] / by_path["Técnica"]),
            ("employees_below_peer_floor", len(recommendations)),
            ("total_recommended_increase", recommendations["recommended_increase"].sum()),
        ],
        columns=["metric", "value"],
    )

    outputs = {
        "department_pay_gap": department_pay_gap,
        "high_salary_by_career": high_salary_by_career,
        "compensation_recommendations": recommendations,
        "analysis_conclusions": conclusions,
    }

    SUBMISSION_DIRECTORY.mkdir(exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(SUBMISSION_DIRECTORY / f"{name}.csv", index=False)


if __name__ == "__main__":
    generate_outputs()
