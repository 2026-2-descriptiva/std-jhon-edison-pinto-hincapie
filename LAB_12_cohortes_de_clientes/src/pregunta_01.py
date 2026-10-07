from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    orders = pd.read_csv("data/sales.csv.gz", usecols=["CustomerID", "OrderDate"])
    month = pd.to_datetime(orders["OrderDate"]).dt.to_period("M")
    cohort = month.groupby(orders["CustomerID"]).transform("min")
    orders["cohort_month"] = cohort.astype(str)
    orders["period_index"] = (month - cohort).apply(lambda offset: offset.n)

    result = (
        orders.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )
    size = result[result["period_index"] == 0].set_index("cohort_month")["active_customers"]
    result["cohort_size"] = result["cohort_month"].map(size)
    result["retention_rate"] = result["active_customers"] / result["cohort_size"]

    Path("submission").mkdir(exist_ok=True)
    result.to_csv("submission/cohort_retention.csv", index=False)

    # Unobserved periods stay NaN (blank in the heatmap), never 0.
    matrix = result.pivot(index="cohort_month", columns="period_index", values="retention_rate")
    fig, ax = plt.subplots(figsize=(9, 6))
    image = ax.imshow(matrix.to_numpy() * 100, cmap="Blues", vmin=0, vmax=100)
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    ax.set_xlabel("Período (meses desde la primera compra)")
    ax.set_ylabel("Cohorte")
    ax.set_title("Retención por cohorte (%)")
    for i, row in enumerate(matrix.to_numpy()):
        for j, value in enumerate(row):
            if pd.notna(value):
                ax.text(j, i, f"{value:.0%}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, label="Retención (%)")
    fig.tight_layout()
    fig.savefig("submission/cohort_retention_heatmap.png", dpi=150)
    plt.close(fig)

    return result
