"""
Finale Locust-Ergebnisanalyse
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript wertet finale Locust-CSV-Dateien mit Wiederholungen aus.

Erwartetes Dateinamenschema:
- postgres_medium_u005_r1_stats.csv
- postgres_medium_u005_r2_stats.csv
- mongo_medium_u100_r3_stats.csv

Ausgegeben werden:
- summary_raw.csv
- summary_aggregated.csv

Beispiel:
python scripts/analyze_final_results.py ^
  --results-dir results/final/medium/raw ^
  --summary-dir results/final/medium/summary
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import defaultdict
from pathlib import Path


# ============================================================
# Pfade
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results" / "final" / "medium" / "raw"
DEFAULT_SUMMARY_DIR = PROJECT_ROOT / "results" / "final" / "medium" / "summary"


# ============================================================
# Dateinamenschema
# ============================================================

FINAL_STATS_PATTERN = re.compile(
    r"^(?P<system>postgres|mongo)_"
    r"(?P<dataset>[A-Za-z0-9_]+)_"
    r"u(?P<users>\d+)_"
    r"r(?P<repetition>\d+)_stats\.csv$"
)


# ============================================================
# Hilfsfunktionen
# ============================================================

def parse_float(value: str | None) -> float:
    if value is None:
        return 0.0

    value = value.strip()

    if value == "":
        return 0.0

    return float(value.replace(",", "."))


def parse_int(value: str | None) -> int:
    if value is None:
        return 0

    value = value.strip()

    if value == "":
        return 0

    return int(float(value.replace(",", ".")))


def mean(values: list[float]) -> float:
    if not values:
        return 0.0

    return statistics.mean(values)


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    return statistics.stdev(values)


def parse_final_stats_filename(path: Path) -> dict:
    """
    Extrahiert Metadaten aus einem finalen Locust-Dateinamen.
    """
    match = FINAL_STATS_PATTERN.match(path.name)

    if not match:
        raise ValueError(
            "Dateiname passt nicht zum erwarteten Schema "
            f"'postgres_medium_u005_r1_stats.csv': {path.name}"
        )

    data = match.groupdict()

    return {
        "system": data["system"],
        "dataset": data["dataset"],
        "users": int(data["users"]),
        "repetition": int(data["repetition"]),
        "run_id": f"{data['system']}_{data['dataset']}_u{int(data['users']):03d}_r{int(data['repetition'])}",
    }


def find_stats_files(results_dir: Path) -> list[Path]:
    """
    Sucht finale Locust *_stats.csv Dateien.
    stats_history.csv wird bewusst ignoriert.
    """
    if not results_dir.exists():
        raise FileNotFoundError(f"Ergebnisordner nicht gefunden: {results_dir}")

    files = sorted(results_dir.glob("*_stats.csv"))

    files = [
        file
        for file in files
        if not file.name.endswith("_stats_history.csv")
    ]

    if not files:
        raise FileNotFoundError(f"Keine *_stats.csv Dateien gefunden in: {results_dir}")

    return files


def read_locust_stats_file(path: Path) -> list[dict]:
    """
    Liest eine einzelne finale Locust stats.csv Datei und ergänzt Metadaten
    aus dem Dateinamen.
    """
    metadata = parse_final_stats_filename(path)
    rows: list[dict] = []

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            request_count = parse_int(row.get("Request Count"))
            failure_count = parse_int(row.get("Failure Count"))

            if request_count > 0:
                failure_rate_percent = (failure_count / request_count) * 100
            else:
                failure_rate_percent = 0.0

            result_row = {
                "system": metadata["system"],
                "dataset": metadata["dataset"],
                "users": metadata["users"],
                "repetition": metadata["repetition"],
                "run_id": metadata["run_id"],
                "type": row.get("Type", ""),
                "operation": row.get("Name", ""),
                "request_count": request_count,
                "failure_count": failure_count,
                "failure_rate_percent": failure_rate_percent,
                "requests_per_second": parse_float(row.get("Requests/s")),
                "failures_per_second": parse_float(row.get("Failures/s")),
                "median_ms": parse_float(row.get("Median Response Time")),
                "avg_ms": parse_float(row.get("Average Response Time")),
                "p95_ms": parse_float(row.get("95%")),
                "p99_ms": parse_float(row.get("99%")),
                "max_ms": parse_float(row.get("Max Response Time")),
                "source_file": path.name,
            }

            rows.append(result_row)

    return rows


def load_all_results(results_dir: Path) -> list[dict]:
    all_rows: list[dict] = []

    for file in find_stats_files(results_dir):
        all_rows.extend(read_locust_stats_file(file))

    return all_rows


def write_csv_file(rows: list[dict], output_path: Path, fieldnames: list[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Gespeichert: {output_path.relative_to(PROJECT_ROOT)}")


def aggregate_rows(rows: list[dict]) -> list[dict]:
    """
    Aggregiert Wiederholungen pro System, Datensatz, Userzahl und Operation.
    Dadurch entstehen Mittelwerte und Standardabweichungen über die Wiederholungen.
    """
    groups: dict[tuple, list[dict]] = defaultdict(list)

    for row in rows:
        key = (
            row["system"],
            row["dataset"],
            row["users"],
            row["type"],
            row["operation"],
        )
        groups[key].append(row)

    metric_names = [
        "request_count",
        "failure_count",
        "failure_rate_percent",
        "requests_per_second",
        "failures_per_second",
        "median_ms",
        "avg_ms",
        "p95_ms",
        "p99_ms",
        "max_ms",
    ]

    aggregated_rows: list[dict] = []

    for key, group_rows in sorted(groups.items(), key=lambda item: item[0]):
        system, dataset, users, request_type, operation = key

        repetitions = sorted({row["repetition"] for row in group_rows})

        aggregated_row = {
            "system": system,
            "dataset": dataset,
            "users": users,
            "type": request_type,
            "operation": operation,
            "repetition_count": len(repetitions),
            "repetitions": ",".join(str(rep) for rep in repetitions),
        }

        for metric in metric_names:
            values = [float(row[metric]) for row in group_rows]

            aggregated_row[f"{metric}_mean"] = mean(values)
            aggregated_row[f"{metric}_std"] = stdev(values)
            aggregated_row[f"{metric}_min"] = min(values) if values else 0.0
            aggregated_row[f"{metric}_max"] = max(values) if values else 0.0

        source_files = sorted({row["source_file"] for row in group_rows})
        aggregated_row["source_files"] = ";".join(source_files)

        aggregated_rows.append(aggregated_row)

    return aggregated_rows


def print_aggregated_overview(aggregated_rows: list[dict]) -> None:
    """
    Gibt eine kurze Übersicht der aggregierten Gesamtergebnisse aus.
    """
    rows = [
        row
        for row in aggregated_rows
        if row["operation"].lower() == "aggregated"
    ]

    if not rows:
        print("\nKeine Aggregated-Zeilen gefunden.")
        return

    print("\nAggregierte Gesamtergebnisse")
    print("-" * 100)
    print(
        f"{'System':<12} {'Dataset':<10} {'Users':>6} {'n':>3} "
        f"{'Req/s':>10} {'Median':>10} {'p95':>10} {'p99':>10} {'Fail %':>10}"
    )
    print("-" * 100)

    for row in sorted(rows, key=lambda r: (r["dataset"], r["users"], r["system"])):
        print(
            f"{row['system']:<12} "
            f"{row['dataset']:<10} "
            f"{row['users']:>6} "
            f"{row['repetition_count']:>3} "
            f"{row['requests_per_second_mean']:>10.2f} "
            f"{row['median_ms_mean']:>10.2f} "
            f"{row['p95_ms_mean']:>10.2f} "
            f"{row['p99_ms_mean']:>10.2f} "
            f"{row['failure_rate_percent_mean']:>10.4f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analysiert finale Locust *_stats.csv Dateien mit Wiederholungen."
    )

    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Ordner mit finalen Locust-Rohdaten. Standard: results/final/medium/raw",
    )

    parser.add_argument(
        "--summary-dir",
        type=Path,
        default=DEFAULT_SUMMARY_DIR,
        help="Zielordner für summary_raw.csv und summary_aggregated.csv.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    results_dir = args.results_dir.resolve()
    summary_dir = args.summary_dir.resolve()

    print("Finale Locust-Ergebnisanalyse")
    print(f"Rohdatenordner: {results_dir}")
    print(f"Summary-Ordner: {summary_dir}")

    raw_rows = load_all_results(results_dir)
    aggregated_rows = aggregate_rows(raw_rows)

    raw_fieldnames = [
        "system",
        "dataset",
        "users",
        "repetition",
        "run_id",
        "type",
        "operation",
        "request_count",
        "failure_count",
        "failure_rate_percent",
        "requests_per_second",
        "failures_per_second",
        "median_ms",
        "avg_ms",
        "p95_ms",
        "p99_ms",
        "max_ms",
        "source_file",
    ]

    metric_names = [
        "request_count",
        "failure_count",
        "failure_rate_percent",
        "requests_per_second",
        "failures_per_second",
        "median_ms",
        "avg_ms",
        "p95_ms",
        "p99_ms",
        "max_ms",
    ]

    aggregated_fieldnames = [
        "system",
        "dataset",
        "users",
        "type",
        "operation",
        "repetition_count",
        "repetitions",
    ]

    for metric in metric_names:
        aggregated_fieldnames.extend(
            [
                f"{metric}_mean",
                f"{metric}_std",
                f"{metric}_min",
                f"{metric}_max",
            ]
        )

    aggregated_fieldnames.append("source_files")

    write_csv_file(
        rows=raw_rows,
        output_path=summary_dir / "summary_raw.csv",
        fieldnames=raw_fieldnames,
    )

    write_csv_file(
        rows=aggregated_rows,
        output_path=summary_dir / "summary_aggregated.csv",
        fieldnames=aggregated_fieldnames,
    )

    print_aggregated_overview(aggregated_rows)

    print("\nAnalyse abgeschlossen.")


if __name__ == "__main__":
    main()
