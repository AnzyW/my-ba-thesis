"""
Finale Locust-Diagrammerzeugung
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript erzeugt Diagramme aus summary_aggregated.csv.

Eingabe:
- results/final/medium/summary/summary_aggregated.csv

Ausgabe:
- results/final/medium/plots/*.png

Beispiel:
python scripts/plot_final_summary.py ^
  --summary-file results/final/medium/summary/summary_aggregated.csv ^
  --plots-dir results/final/medium/plots
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# Pfade
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY_FILE = PROJECT_ROOT / "results" / "final" / "medium" / "summary" / "summary_aggregated.csv"
DEFAULT_PLOTS_DIR = PROJECT_ROOT / "results" / "final" / "medium" / "plots"


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


def system_label(system: str) -> str:
    labels = {
        "postgres": "PostgreSQL",
        "mongo": "MongoDB",
    }

    return labels.get(system, system)


def read_aggregated_summary(summary_file: Path) -> list[dict]:
    if not summary_file.exists():
        raise FileNotFoundError(f"summary_aggregated.csv nicht gefunden: {summary_file}")

    rows: list[dict] = []

    with summary_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            parsed_row = {
                "system": row["system"],
                "dataset": row["dataset"],
                "users": parse_int(row["users"]),
                "type": row["type"],
                "operation": row["operation"],
                "repetition_count": parse_int(row["repetition_count"]),
                "requests_per_second_mean": parse_float(row["requests_per_second_mean"]),
                "requests_per_second_std": parse_float(row["requests_per_second_std"]),
                "median_ms_mean": parse_float(row["median_ms_mean"]),
                "median_ms_std": parse_float(row["median_ms_std"]),
                "p95_ms_mean": parse_float(row["p95_ms_mean"]),
                "p95_ms_std": parse_float(row["p95_ms_std"]),
                "p99_ms_mean": parse_float(row["p99_ms_mean"]),
                "p99_ms_std": parse_float(row["p99_ms_std"]),
                "max_ms_mean": parse_float(row["max_ms_mean"]),
                "max_ms_std": parse_float(row["max_ms_std"]),
                "failure_count_mean": parse_float(row["failure_count_mean"]),
                "failure_count_std": parse_float(row["failure_count_std"]),
                "failure_rate_percent_mean": parse_float(row["failure_rate_percent_mean"]),
                "failure_rate_percent_std": parse_float(row["failure_rate_percent_std"]),
            }

            rows.append(parsed_row)

    return rows


def get_aggregated_operation_rows(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in rows
        if row["operation"].lower() == "aggregated"
    ]


def get_sorted_users(rows: list[dict]) -> list[int]:
    return sorted({row["users"] for row in rows})


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


def get_metric_value(rows: list[dict], system: str, users: int, metric: str) -> float:
    for row in rows:
        if row["system"] == system and row["users"] == users:
            return float(row[metric])

    return 0.0


def plot_metric_by_users(
    rows: list[dict],
    metric_mean: str,
    metric_std: str,
    title: str,
    y_label: str,
    output_filename: str,
    plots_dir: Path,
) -> None:
    """
    Erstellt ein Liniendiagramm über die Laststufen.
    Optional werden Standardabweichungen als Fehlerbalken angezeigt.
    """
    plots_dir.mkdir(parents=True, exist_ok=True)

    users_values = get_sorted_users(rows)
    systems = get_systems(rows)

    plt.figure(figsize=(10, 6))

    for system in systems:
        y_values = [
            get_metric_value(rows, system, users, metric_mean)
            for users in users_values
        ]

        y_errors = [
            get_metric_value(rows, system, users, metric_std)
            for users in users_values
        ]

        plt.errorbar(
            users_values,
            y_values,
            yerr=y_errors,
            marker="o",
            capsize=4,
            label=system_label(system),
        )

    plt.title(title)
    plt.xlabel("Locust-User")
    plt.ylabel(y_label)
    plt.xticks(users_values)
    plt.grid(True, axis="y", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.ylim(bottom=0)
    plt.tight_layout()

    output_path = plots_dir / output_filename
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Diagramm gespeichert: {output_path.relative_to(PROJECT_ROOT)}")


def plot_operation_p95_at_max_users(
    rows: list[dict],
    plots_dir: Path,
) -> None:
    """
    Erstellt ein operationsbezogenes p95-Diagramm für die höchste gemessene Laststufe.
    Die Aggregated-Zeile wird dabei ausgeschlossen.
    """
    plots_dir.mkdir(parents=True, exist_ok=True)

    operation_rows = [
        row
        for row in rows
        if row["operation"].lower() != "aggregated"
    ]

    if not operation_rows:
        print("Keine operationsbezogenen Zeilen für p95-Detaildiagramm gefunden.")
        return

    max_users = max(row["users"] for row in operation_rows)

    selected_rows = [
        row
        for row in operation_rows
        if row["users"] == max_users
    ]

    operations = sorted({row["operation"] for row in selected_rows})
    systems = get_systems(selected_rows)

    x_values = list(range(len(operations)))
    width = 0.8 / max(len(systems), 1)

    plt.figure(figsize=(12, 6))

    for index, system in enumerate(systems):
        y_values = []

        for operation in operations:
            value = 0.0

            for row in selected_rows:
                if row["system"] == system and row["operation"] == operation:
                    value = row["p95_ms_mean"]
                    break

            y_values.append(value)

        shifted_x_values = [
            x + (index - (len(systems) - 1) / 2) * width
            for x in x_values
        ]

        plt.bar(
            shifted_x_values,
            y_values,
            width=width,
            label=system_label(system),
        )

    plt.title(f"p95-Latenz je Operation bei {max_users} Locust-Usern")
    plt.xlabel("Operation")
    plt.ylabel("p95-Latenz in ms")
    plt.xticks(x_values, operations, rotation=30, ha="right")
    plt.grid(True, axis="y", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.ylim(bottom=0)
    plt.tight_layout()

    output_path = plots_dir / f"operation_p95_u{max_users:03d}.png"
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Diagramm gespeichert: {output_path.relative_to(PROJECT_ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Erzeugt finale Diagramme aus summary_aggregated.csv."
    )

    parser.add_argument(
        "--summary-file",
        type=Path,
        default=DEFAULT_SUMMARY_FILE,
        help="Pfad zur summary_aggregated.csv.",
    )

    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=DEFAULT_PLOTS_DIR,
        help="Zielordner für Diagramme.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    summary_file = args.summary_file.resolve()
    plots_dir = args.plots_dir.resolve()

    print("Finale Diagrammerzeugung")
    print(f"Summary-Datei: {summary_file}")
    print(f"Plot-Ordner: {plots_dir}")

    rows = read_aggregated_summary(summary_file)
    aggregated_rows = get_aggregated_operation_rows(rows)

    if not aggregated_rows:
        raise RuntimeError("Keine Aggregated-Zeilen in summary_aggregated.csv gefunden.")

    plot_metric_by_users(
        rows=aggregated_rows,
        metric_mean="requests_per_second_mean",
        metric_std="requests_per_second_std",
        title="Durchsatz je Laststufe",
        y_label="Requests pro Sekunde",
        output_filename="throughput_by_users.png",
        plots_dir=plots_dir,
    )

    plot_metric_by_users(
        rows=aggregated_rows,
        metric_mean="median_ms_mean",
        metric_std="median_ms_std",
        title="Median-Latenz je Laststufe",
        y_label="Latenz in ms",
        output_filename="median_latency_by_users.png",
        plots_dir=plots_dir,
    )

    plot_metric_by_users(
        rows=aggregated_rows,
        metric_mean="p95_ms_mean",
        metric_std="p95_ms_std",
        title="p95-Latenz je Laststufe",
        y_label="Latenz in ms",
        output_filename="p95_latency_by_users.png",
        plots_dir=plots_dir,
    )

    plot_metric_by_users(
        rows=aggregated_rows,
        metric_mean="p99_ms_mean",
        metric_std="p99_ms_std",
        title="p99-Latenz je Laststufe",
        y_label="Latenz in ms",
        output_filename="p99_latency_by_users.png",
        plots_dir=plots_dir,
    )

    plot_metric_by_users(
        rows=aggregated_rows,
        metric_mean="failure_rate_percent_mean",
        metric_std="failure_rate_percent_std",
        title="Fehlerrate je Laststufe",
        y_label="Fehlerrate in %",
        output_filename="failure_rate_by_users.png",
        plots_dir=plots_dir,
    )

    plot_operation_p95_at_max_users(
        rows=rows,
        plots_dir=plots_dir,
    )

    print("\nDiagrammerzeugung abgeschlossen.")


if __name__ == "__main__":
    main()
