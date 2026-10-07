def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        4
    """

    import pandas as pd

    return pd.read_csv("data/tbl0.tsv", sep="\t").shape[1]
