import gzip


def _read_rows():
    with gzip.open("data/data.csv.gz", "rt") as f:
        return [line.rstrip("\n").split("\t") for line in f if line.strip()]


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """

    values = {}
    for row in _read_rows():
        values.setdefault(row[0], []).append(int(row[1]))
    return [(k, max(v), min(v)) for k, v in sorted(values.items())]
