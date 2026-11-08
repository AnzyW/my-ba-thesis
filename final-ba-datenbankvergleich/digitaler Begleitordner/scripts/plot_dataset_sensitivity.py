"""
Diagramme für die Datenmengen-Sensitivitätsanalyse.

Verglichen werden bei konstant 500 Locust-Usern:

- medium: 50.000 Produkte
- large_catalog: 200.000 Produkte

Beide Varianten liegen für PostgreSQL und MongoDB mit jeweils n=3 vor.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_COMPARISON_FILE = (
    PROJECT_ROOT
    / "results"
    / "large_catalog"
    / "summary"
    / "dataset_sensitivity_comparison.csv"
)

DEFAULT_PLOTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "large_catalog"
    / "plots"
)

SYSTEM_ORDER = ["postgres", "mongo"]

SYSTEM_LABELS = {
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
}


def parse_float(value: str | None) -> float:
    if value is None or value.strip() == "":
        return 0.0

    return float(value.replace(",", "."))


def read_comparison_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Vergleichsdatei nicht gefunden: {path}"
        )

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise RuntimeError(
            f"Die Vergleichsdatei enthält keine Daten: {path}"
        )

    rows_by_system = {
        row["system"]: row
        for row in rows
    }

    missing_systems = [
        system
        for system in SYSTEM_ORDER
        if system not in rows_by_system
    ]

    if missing_systems:
        raise RuntimeError(
            "Fehlende Systeme in der Vergleichsdatei: "
            + ", ".join(missing_systems)
        )

    return [
        rows_by_system[system]
        for system in SYSTEM_ORDER
    ]


def plot_metric(
    rows: list[dict[str, str]],
    plots_dir: Path,
    medium_key: str,
    large_catalog_key: str,
    title: str,
    ylabel: str,
    filename: str,
    divisor: float = 1.0,
    decimals: int = 1,
) -> None:
    systems = [
        SYSTEM_LABELS.get(row["system"], row["system"])
        for row in rows
    ]

    medium_values = [
        parse_float(row[medium_key]) / divisor
        for row in rows
    ]

    large_catalog_values = [
        parse_float(row[large_catalog_key]) / divisor
        for row in rows
    ]

    x_positions = list(range(len(systems)))
    bar_width = 0.36

    figure, axis = plt.subplots(figsize=(8.5, 5.2))

    medium_positions = [
        position - bar_width / 2
        for position in x_positions
    ]

    large_catalog_positions = [
        position + bar_width / 2
        for position in x_positions
    ]

    medium_bars = axis.bar(
        medium_positions,
        medium_values,
        width=bar_width,
        label="Medium (50.000 Produkte)",
    )

    large_catalog_bars = axis.bar(
        large_catalog_positions,
        large_catalog_values,
        width=bar_width,
        label="Large Catalog (200.000 Produkte)",
    )

    value_format = f"{{:.{decimals}f}}"

    axis.bar_label(
        medium_bars,
        labels=[
            value_format.format(value)
            for value in medium_values
        ],
        padding=3,
        fontsize=8,
    )

    axis.bar_label(
        large_catalog_bars,
        labels=[
            value_format.format(value)
            for value in large_catalog_values
        ],
        padding=3,
        fontsize=8,
    )

    axis.set_title(
        f"Datenmengen-Sensitivität bei 500 Usern: {title}\n"
        "(je Datensatz und System n=3)"
    )
    axis.set_xlabel("Datenbanksystem")
    axis.set_ylabel(ylabel)
    axis.set_xticks(x_positions)
    axis.set_xticklabels(systems)
    axis.grid(True, axis="y", alpha=0.3)
    axis.legend()

    maximum = max(
        medium_values + large_catalog_values
    )

    if maximum > 0:
        axis.set_ylim(0, maximum * 1.18)

    figure.tight_layout()

    plots_dir.mkdir(parents=True, exist_ok=True)
    output_path = plots_dir / filename

    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    print(f"Gespeichert: {output_path.relative_to(PROJECT_ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Erzeugt Diagramme für die Datenmengen-"
            "Sensitivitätsanalyse."
        )
    )

    parser.add_argument(
        "--comparison-file",
        type=Path,
        default=DEFAULT_COMPARISON_FILE,
        help="Pfad zur dataset_sensitivity_comparison.csv.",
    )

    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=DEFAULT_PLOTS_DIR,
        help="Zielordner für die Diagramme.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    comparison_file = args.comparison_file.resolve()
    plots_dir = args.plots_dir.resolve()

    rows = read_comparison_rows(comparison_file)

    plot_metric(
        rows=rows,
        plots_dir=plots_dir,
        medium_key="medium_rps",
        large_catalog_key="large_catalog_rps",
        title="Durchsatz",
        ylabel="Requests pro Sekunde",
        filename="dataset_sensitivity_throughput.png",
        decimals=1,
    )

    plot_metric(
        rows=rows,
        plots_dir=plots_dir,
        medium_key="medium_median_ms",
        large_catalog_key="large_catalog_median_ms",
        title="Median-Latenz",
        ylabel="Antwortzeit in Sekunden",
        filename="dataset_sensitivity_median_latency.png",
        divisor=1000.0,
        decimals=2,
    )

    plot_metric(
        rows=rows,
        plots_dir=plots_dir,
        medium_key="medium_p95_ms",
        large_catalog_key="large_catalog_p95_ms",
        title="p95-Latenz",
        ylabel="Antwortzeit in Sekunden",
        filename="dataset_sensitivity_p95_latency.png",
        divisor=1000.0,
        decimals=2,
    )

    plot_metric(
        rows=rows,
        plots_dir=plots_dir,
        medium_key="medium_p99_ms",
        large_catalog_key="large_catalog_p99_ms",
        title="p99-Latenz",
        ylabel="Antwortzeit in Sekunden",
        filename="dataset_sensitivity_p99_latency.png",
        divisor=1000.0,
        decimals=2,
    )

    print("Diagramme der Datenmengen-Sensitivitätsanalyse erfolgreich erzeugt.")


if __name__ == "__main__":
    main()