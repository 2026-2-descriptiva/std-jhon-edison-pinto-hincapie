import pandas as pd


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    df = pd.read_csv("data/solicitudes_de_credito.csv.gz", sep=";", dtype=str)
    df = df.drop(columns="Unnamed: 0")

    text_cols = ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito"]
    for col in text_cols:
        df[col] = (
            df[col]
            .str.lower()
            .str.replace(r"[-_]", " ", regex=True)
            .str.split()
            .str.join(" ")
        )

    df["estrato"] = df["estrato"].astype(int)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype(float).astype("Int64")
    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .str.replace(r"\.00$", "", regex=True)
        .str.replace(r"[^0-9]", "", regex=True)
        .astype("int64")
    )

    # dos formatos de fecha: dd/mm/aaaa y aaaa/mm/dd
    dates = pd.to_datetime(df["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce")
    dates = dates.fillna(
        pd.to_datetime(df["fecha_de_beneficio"], format="%Y/%m/%d", errors="coerce")
    )
    df["fecha_de_beneficio"] = dates.dt.strftime("%Y-%m-%d")

    # comuna faltante es dato original; el resto de faltantes se descarta
    df = df.dropna(subset=[c for c in df.columns if c != "comuna_ciudadano"])
    df = df.drop_duplicates()

    df.to_csv("submission/solicitudes_de_credito.csv", sep=";", index=False)
