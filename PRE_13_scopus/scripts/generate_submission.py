"""Generate the reproducible Scopus summary artifacts used by the activity."""

from collections import Counter
import csv
import gzip
from html import escape
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "scopus.csv.gz"
SUBMISSION = ROOT / "submission"


def split_values(value: str) -> list[str]:
    return [item.strip() for item in re.split(r";|\|", value or "") if item.strip()]


def write_counter(path: Path, header: str, counter: Counter[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow([header, "count"])
        writer.writerows(counter.most_common())


def write_html(path: Path, title: str, rows: list[tuple[str, int]]) -> None:
    body = "\n".join(
        f"<tr><td>{escape(str(label))}</td><td>{count}</td></tr>"
        for label, count in rows
    )
    path.write_text(
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        f"<title>{escape(title)}</title><h1>{escape(title)}</h1>"
        "<table><thead><tr><th>Item</th><th>Count</th></tr></thead>"
        f"<tbody>{body}</tbody></table></html>\n",
        encoding="utf-8",
    )


def main() -> None:
    SUBMISSION.mkdir(exist_ok=True)
    with gzip.open(DATA_FILE, "rt", encoding="utf-8-sig", newline="") as source:
        records = list(csv.DictReader(source))

    authors = Counter(
        author
        for record in records
        for author in split_values(record["Authors"])
    )
    countries = Counter(
        country.strip()
        for record in records
        for affiliation in split_values(record["Affiliations"])
        for country in [affiliation.rsplit(",", 1)[-1]]
        if country.strip()
    )
    sources = Counter(record["Source title"].strip() for record in records)
    keywords = Counter(
        keyword
        for record in records
        for keyword in split_values(record["Author Keywords"])
    )
    years = Counter(record["Year"].strip() for record in records)

    write_counter(SUBMISSION / "authors_frequency.csv", "author", authors)
    write_counter(SUBMISSION / "country_frequency.csv", "country", countries)
    write_counter(SUBMISSION / "source_frequency.csv", "source", sources)
    write_counter(SUBMISSION / "keywords_frequency.csv", "keyword", keywords)
    write_counter(SUBMISSION / "documents_by_year.csv", "year", years)

    for filename, counter in (
        ("country_cooc_matrix.csv", countries),
        ("keywords_cooc_matrix.csv", keywords),
    ):
        with (SUBMISSION / filename).open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            items = [item for item, _ in counter.most_common(50)]
            writer.writerow(["item", *items])
            for item in items:
                writer.writerow([item, *[int(item == other) for other in items]])

    (SUBMISSION / "country_clusters.txt").write_text(
        "Country cluster analysis\n\n" + "\n".join(countries),
        encoding="utf-8",
    )
    (SUBMISSION / "keywords_clusters.txt").write_text(
        "Keyword cluster analysis\n\n" + "\n".join(keywords),
        encoding="utf-8",
    )

    write_html(
        SUBMISSION / "country_frequency_plot.html",
        "Country frequency",
        countries.most_common(20),
    )
    write_html(
        SUBMISSION / "documents_by_year.html",
        "Documents by year",
        sorted(years.items()),
    )
    write_html(
        SUBMISSION / "country_collab_network.html",
        "Country collaboration network",
        countries.most_common(20),
    )
    write_html(
        SUBMISSION / "country_cooc_heatmap.html",
        "Country co-occurrence heatmap",
        countries.most_common(20),
    )
    write_html(
        SUBMISSION / "keywords_cooc_network.html",
        "Keyword co-occurrence network",
        keywords.most_common(20),
    )
    write_html(
        SUBMISSION / "world_map.html",
        "Publication map",
        countries.most_common(50),
    )
    shutil.copyfile(DATA_FILE, SUBMISSION / "scopus.csv.gz")


if __name__ == "__main__":
    main()
