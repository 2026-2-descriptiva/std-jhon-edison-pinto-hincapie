import gzip


def _read_rows():
    with gzip.open("data/data.csv.gz", "rt") as f:
        return [line.rstrip("\n").split("\t") for line in f if line.strip()]


def pregunta_07():
    """
    Para cada valor distinto de la segunda columna (`value`), construya la
    lista de letras de la primera columna (`letter`) que aparecen con ese
    valor. Conserve las letras repetidas y el orden en que aparecen en el
    archivo. Retorne una lista de tuplas `(valor, letras)` ordenada por el
    valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["E", "B", "E"]), (2, ["A", "E"]), ...]
    """

    letters = {}
    for row in _read_rows():
        letters.setdefault(int(row[1]), []).append(row[0])
    return sorted(letters.items())
