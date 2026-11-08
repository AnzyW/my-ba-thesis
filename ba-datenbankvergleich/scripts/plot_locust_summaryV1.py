"""
Locust Diagrammerzeugung V1
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript liest results/smoke/summary.csv ein und erzeugt erste Diagramme
für die Smoke- und Probeläufe.

Die Diagramme dienen zunächst zur Prüfung der Auswertungspipeline.
Sie sind noch keine finalen Ergebnisdiagramme für die Bachelorarbeit.

Erzeugte Diagramme:
- throughput_by_run.png
- median_latency_by_run.png
- p95_latency_by_run.png
- p99_latency_by_run.png
- max_latency_by_run.png
- failures_by_run.png
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# Pfade
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "smoke"
SUMMARY_FILE = RESULTS_DIR / "summary.csv"
PLOTS_DIR = RESULTS_DIR / "plots"


# ============================================================
# Hilfsfunktionen
# ============================================================

def parse_float(value: str) -> float:
    if value is None:
        return 0.0

    value = value.strip()

    if value == "":
        return 0.0

    return float(value.replace(",", "."))


def parse_int(value: str) -> int:
    if value is None:
        return 0

    value = value.strip()

    if value == "":
        return 0

    return int(float(value.replace(",", ".")))


def run_sort_key(run_name: str) -> tuple[int, int]:
    """
    Sortiert Läufe sinnvoll:
    - v1 zuerst
    - probe_u5 danach
    - probe_u10 danach
    - spätere probe_u25, probe_u50 usw. automatisch danach
    """
    if run_name == "v1":
        return 0, 1

    match = re.search(r"u(\d+)", run_name)

    if match:
        return 1, int(match.group(1))

    return 2, 0


def run_label(run_name: str) -> str:
    """
    Wandelt technische Run-Namen in lesbare Achsenbeschriftungen um.
    """
    if run_name == "v1":
        return "Smoke V1"

    match = re.search(r"u(\d+)", run_name)

    if match:
        return f"{match.group(1)} User"

    return run_name


def read_summary_rows() -> list[dict]:
    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"summary.csv nicht gefunden: {SUMMARY_FILE}\n"
            "Bitte zuerst ausführen: python scripts/analyze_locust_results.py"
        )

    rows = []

    with SUMMARY_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            parsed_row = {
                "system": row["system"],
                "run": row["run"],
                "type": row["type"],
                "operation": row["operation"],
                "request_count": parse_int(row["request_count"]),
                "failure_count": parse_int(row["failure_count"]),
                "requests_per_second": parse_float(row["requests_per_second"]),
                "failures_per_second": parse_float(row["failures_per_second"]),
                "median_ms": parse_float(row["median_ms"]),
                "avg_ms": parse_float(row["avg_ms"]),
                "p95_ms": parse_float(row["p95_ms"]),
                "p99_ms": parse_float(row["p99_ms"]),
                "max_ms": parse_float(row["max_ms"]),
                "source_file": row["source_file"],
            }

            rows.append(parsed_row)

    return rows


def get_aggregated_rows(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in rows
        if row["operation"].lower() == "aggregated"
    ]


def get_sorted_runs(rows: list[dict]) -> list[str]:
    runs = sorted(
        {row["run"] for row in rows},
        key=run_sort_key,
    )

    return runs


def get_systems(rows: list[dict]) -> list[str]:
    preferred_order = ["postgres", "mongo"]
    systems = {row["system"] for row in rows}

    ordered_systems = [
        system
        for system in preferred_order
        if system in systems
    ]

    remaining_systems = sorted(systems - set(ordered_systems))

    return ordered_systems + remaining_systems


def get_metric_value(rows: list[dict], system: str, run: str, metric: str) -> float:
    for row in rows:
        if row["system"] == system and row["run"] == run:
            return float(row[metric])

    return 0.0


def plot_metric(
    rows: list[dict],
    metric: str,
    title: str,
    y_label: str,
    output_filename: str,
) -> None:
    """
    Erstellt ein Liniendiagramm für eine Metrik.
    Pro Datenbanksystem wird eine eigene Linie gezeichnet.
    """
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    runs = get_sorted_runs(rows)
    systems = get_systems(rows)

    x_values = list(range(len(runs)))
    x_labels = [run_label(run) for run in runs]

    plt.figure(figsize=(10, 6))

    for system in systems:
        y_values = [
            get_metric_value(rows, system, run, metric)
            for run in runs
        ]

        plt.plot(
            x_values,
            y_values,
            marker="o",
            label=system,
        )

    plt.title(title)
    plt.xlabel("Probelauf")
    plt.ylabel(y_label)
    plt.xticks(x_values, x_labels)
    plt.grid(True, axis="y", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    output_path = PLOTS_DIR / output_filename
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Diagramm gespeichert: {output_path.relative_to(PROJECT_ROOT)}")


# ============================================================
# Hauptprogramm
# ============================================================

def main() -> None:
    print("Erzeuge Locust-Diagramme...")
    print(f"Eingabedatei: {SUMMARY_FILE}")

    rows = read_summary_rows()
    aggregated_rows = get_aggregated_rows(rows)

    if not aggregated_rows:
        raise RuntimeError("Keine Aggregated-Zeilen in summary.csv gefunden.")

    plot_metric(
        rows=aggregated_rows,
        metric="requests_per_second",
        title="Durchsatz je Probelauf",
        y_label="Requests pro Sekunde",
        output_filename="throughput_by_run.png",
    )

    plot_metric(
        rows=aggregated_rows,
        metric="median_ms",
        title="Median-Latenz je Probelauf",
        y_label="Latenz in ms",
        output_filename="median_latency_by_run.png",
    )

    plot_metric(
        rows=aggregated_rows,
        metric="p95_ms",
        title="p95-Latenz je Probelauf",
        y_label="Latenz in ms",
        output_filename="p95_latency_by_run.png",
    )

    plot_metric(
        rows=aggregated_rows,
        metric="p99_ms",
        title="p99-Latenz je Probelauf",
        y_label="Latenz in ms",
        output_filename="p99_latency_by_run.png",
    )

    plot_metric(
        rows=aggregated_rows,
        metric="max_ms",
        title="Maximale Antwortzeit je Probelauf",
        y_label="Latenz in ms",
        output_filename="max_latency_by_run.png",
    )

    plot_metric(
        rows=aggregated_rows,
        metric="failure_count",
        title="Fehleranzahl je Probelauf",
        y_label="Anzahl Fehler",
        output_filename="failures_by_run.png",
    )

    print("\nDiagrammerzeugung abgeschlossen.")


if __name__ == "__main__":
    main()