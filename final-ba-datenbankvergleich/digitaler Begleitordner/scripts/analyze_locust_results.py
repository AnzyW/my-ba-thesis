"""
Locust Ergebnisanalyse V1
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript liest Locust-CSV-Dateien aus dem Ordner results/smoke/ ein
und erzeugt eine kompakte Übersicht über die wichtigsten Kennzahlen.

Ausgewertet werden:
- Request Count
- Failure Count
- Requests/s
- Failures/s
- Median Response Time
- Average Response Time
- p95
- p99
- Max Response Time

Das Skript dient zunächst zur Plausibilitätsprüfung der Smoke- und Probeläufe.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


# ============================================================
# Pfade
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results" / "smoke"


# ============================================================
# Hilfsfunktionen
# ============================================================

def parse_float(value: str) -> float:
    """
    Wandelt einen CSV-Wert robust in float um.
    Leere Werte werden als 0.0 interpretiert.
    """
    if value is None:
        return 0.0

    value = value.strip()

    if value == "":
        return 0.0

    return float(value.replace(",", "."))


def parse_int(value: str) -> int:
    """
    Wandelt einen CSV-Wert robust in int um.
    """
    if value is None:
        return 0

    value = value.strip()

    if value == "":
        return 0

    return int(float(value.replace(",", ".")))


def parse_result_filename(path: Path) -> tuple[str, str]:
    """
    Zerlegt Dateinamen wie:
    - postgres_v1_stats.csv
    - mongo_probe_u10_stats.csv

    Rückgabe:
    - system: postgres oder mongo
    - run_name: v1, probe_u10 usw.
    """
    name = path.name

    if not name.endswith("_stats.csv"):
        raise ValueError(f"Keine Locust stats.csv Datei: {name}")

    base_name = name.replace("_stats.csv", "")
    parts = base_name.split("_", 1)

    if len(parts) == 1:
        return parts[0], "unknown"

    return parts[0], parts[1]


def read_locust_stats_file(path: Path) -> list[dict]:
    """
    Liest eine einzelne Locust *_stats.csv Datei.
    """
    system, run_name = parse_result_filename(path)

    rows = []

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            operation_name = row.get("Name", "")

            result_row = {
                "system": system,
                "run": run_name,
                "type": row.get("Type", ""),
                "operation": operation_name,
                "request_count": parse_int(row.get("Request Count", "0")),
                "failure_count": parse_int(row.get("Failure Count", "0")),
                "requests_per_second": parse_float(row.get("Requests/s", "0")),
                "failures_per_second": parse_float(row.get("Failures/s", "0")),
                "median_ms": parse_float(row.get("Median Response Time", "0")),
                "avg_ms": parse_float(row.get("Average Response Time", "0")),
                "p95_ms": parse_float(row.get("95%", "0")),
                "p99_ms": parse_float(row.get("99%", "0")),
                "max_ms": parse_float(row.get("Max Response Time", "0")),
                "source_file": path.name,
            }

            rows.append(result_row)

    return rows


def find_stats_files(results_dir: Path) -> list[Path]:
    """
    Sucht alle Locust stats.csv Dateien.
    """
    if not results_dir.exists():
        raise FileNotFoundError(f"Ergebnisordner nicht gefunden: {results_dir}")

    files = sorted(results_dir.glob("*_stats.csv"))

    # stats_history.csv soll nicht als normale stats.csv interpretiert werden.
    files = [
        file
        for file in files
        if not file.name.endswith("_stats_history.csv")
    ]

    return files


def load_all_results(results_dir: Path) -> list[dict]:
    """
    Lädt alle gefundenen Locust-Statistikdateien.
    """
    stats_files = find_stats_files(results_dir)

    if not stats_files:
        raise FileNotFoundError(f"Keine *_stats.csv Dateien gefunden in: {results_dir}")

    all_rows = []

    for file in stats_files:
        all_rows.extend(read_locust_stats_file(file))

    return all_rows


def get_aggregated_rows(rows: list[dict]) -> list[dict]:
    """
    Filtert die Aggregated-Zeilen aus Locust heraus.
    Diese Zeilen enthalten die zusammengefassten Werte pro Lauf.
    """
    return [
        row
        for row in rows
        if row["operation"].lower() == "aggregated"
    ]


def print_table(rows: list[dict], title: str) -> None:
    """
    Gibt eine einfache Tabelle im Terminal aus.
    """
    if not rows:
        print(f"\n{title}")
        print("Keine Daten vorhanden.")
        return

    columns = [
        ("system", "System"),
        ("run", "Run"),
        ("operation", "Operation"),
        ("request_count", "Requests"),
        ("failure_count", "Failures"),
        ("requests_per_second", "Req/s"),
        ("median_ms", "Median ms"),
        ("avg_ms", "Avg ms"),
        ("p95_ms", "p95 ms"),
        ("p99_ms", "p99 ms"),
        ("max_ms", "Max ms"),
    ]

    table_data = []

    for row in rows:
        table_row = []

        for key, _label in columns:
            value = row[key]

            if isinstance(value, float):
                table_row.append(f"{value:.2f}")
            else:
                table_row.append(str(value))

        table_data.append(table_row)

    headers = [label for _key, label in columns]

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in table_data))
        for index in range(len(headers))
    ]

    print(f"\n{title}")
    print("-" * sum(widths) + "-" * (3 * (len(widths) - 1)))

    header_line = " | ".join(
        headers[index].ljust(widths[index])
        for index in range(len(headers))
    )
    print(header_line)

    print("-" * len(header_line))

    for row in table_data:
        line = " | ".join(
            row[index].ljust(widths[index])
            for index in range(len(row))
        )
        print(line)


def write_summary_csv(rows: list[dict], output_path: Path) -> None:
    """
    Schreibt alle eingelesenen Kennzahlen in eine zusammenfassende CSV-Datei.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "system",
        "run",
        "type",
        "operation",
        "request_count",
        "failure_count",
        "requests_per_second",
        "failures_per_second",
        "median_ms",
        "avg_ms",
        "p95_ms",
        "p99_ms",
        "max_ms",
        "source_file",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nZusammenfassung gespeichert: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analysiert Locust *_stats.csv Dateien."
    )

    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Ordner mit Locust CSV-Dateien. Standard: results/smoke",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULTS_DIR / "summary.csv",
        help="Pfad zur zusammenfassenden CSV-Datei.",
    )

    return parser.parse_args()


# ============================================================
# Hauptprogramm
# ============================================================

def main() -> None:
    args = parse_args()

    results_dir = args.results_dir.resolve()
    output_path = args.output.resolve()

    print("Locust Ergebnisanalyse")
    print(f"Ergebnisordner: {results_dir}")

    rows = load_all_results(results_dir)
    aggregated_rows = get_aggregated_rows(rows)

    print_table(
        aggregated_rows,
        "Aggregierte Ergebnisse je Lauf",
    )

    operation_rows = [
        row
        for row in rows
        if row["operation"].lower() != "aggregated"
    ]

    print_table(
        operation_rows,
        "Ergebnisse je Operation",
    )

    write_summary_csv(rows, output_path)


if __name__ == "__main__":
    main()