import gzip


def _read_rows():
    with gzip.open("data/data.csv.gz", "rt") as f:
        return [line.rstrip("\n").split("\t") for line in f if line.strip()]


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """

    letters = {}
    for row in _read_rows():
        letters.setdefault(int(row[1]), set()).add(row[0])
    return [(k, sorted(v)) for k, v in sorted(letters.items())]
