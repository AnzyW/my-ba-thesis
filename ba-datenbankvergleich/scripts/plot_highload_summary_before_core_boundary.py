from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


DEFAULT_SUMMARY_FILE = Path(
    "results/highload/validated_highload_summary.csv"
)
DEFAULT_PLOTS_DIR = Path("results/highload/plots")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Erzeugt Diagramme aus der validierten "
            "Hochlastübersicht."
        )
    )
    parser.add_argument(
        "--summary-file",
        type=Path,
        default=DEFAULT_SUMMARY_FILE,
        help="Pfad zur validated_highload_summary.csv.",
    )
    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=DEFAULT_PLOTS_DIR,
        help="Zielordner für die Diagramme.",
    )
    return parser.parse_args()


def read_rows(summary_file: Path) -> list[dict[str, str | int | float]]:
    if not summary_file.exists():
        raise FileNotFoundError(
            f"Datei nicht gefunden: {summary_file}"
        )

    rows: list[dict[str, str | int | float]] = []

    with summary_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "system",
            "users",
            "requests_per_second",
            "median_ms",
            "p95_ms",
            "p99_ms",
            "fail_rate_percent",
        }

        available_columns = set(reader.fieldnames or [])
        missing_columns = required_columns - available_columns

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Fehlende Spalten: {missing}")

        for row in reader:
            rows.append(
                {
                    "system": row["system"].strip().lower(),
                    "users": int(row["users"]),
                    "requests_per_second": float(
                        row["requests_per_second"]
                    ),
                    "median_ms": float(row["median_ms"]),
                    "p95_ms": float(row["p95_ms"]),
                    "p99_ms": float(row["p99_ms"]),
                    "fail_rate_percent": float(
                        row["fail_rate_percent"]
                    ),
                }
            )

    if not rows:
        raise ValueError(
            "Die Hochlastübersicht enthält keine Datenzeilen."
        )

    return rows


def system_label(system: str) -> str:
    labels = {
        "postgres": "PostgreSQL",
        "mongo": "MongoDB",
    }
    return labels.get(system, system)


def plot_metric(
    rows: list[dict[str, str | int | float]],
    plots_dir: Path,
    metric: str,
    ylabel: str,
    title: str,
    filename: str,
    divisor: float = 1.0,
) -> None:
    plt.figure(figsize=(8.5, 5.2))

    systems = sorted(
        {
            str(row["system"])
            for row in rows
        }
    )

    for system in systems:
        selected = sorted(
            (
                row
                for row in rows
                if row["system"] == system
            ),
            key=lambda row: int(row["users"]),
        )

        x_values = [
            int(row["users"])
            for row in selected
        ]

        y_values = [
            float(row[metric]) / divisor
            for row in selected
        ]

        plt.plot(
            x_values,
            y_values,
            marker="o",
            linewidth=2,
            label=system_label(system),
        )

    user_values = sorted(
        {
            int(row["users"])
            for row in rows
        }
    )

    plt.title(title)
    plt.xlabel("Simulierte Locust-User")
    plt.ylabel(ylabel)
    plt.xticks(user_values)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path = plots_dir / filename

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Gespeichert: {output_path}")

def plot_failure_rate(
    rows: list[dict[str, str | int | float]],
    plots_dir: Path,
) -> None:
    systems = sorted(
        {
            str(row["system"])
            for row in rows
        }
    )

    user_values = sorted(
        {
            int(row["users"])
            for row in rows
        }
    )

    x_positions = list(range(len(user_values)))
    bar_width = 0.36

    figure, axis = plt.subplots(figsize=(8.5, 5.2))

    for system_index, system in enumerate(systems):
        selected = {
            int(row["users"]): float(row["fail_rate_percent"])
            for row in rows
            if row["system"] == system
        }

        offset = (
            system_index - (len(systems) - 1) / 2
        ) * bar_width

        bar_positions = [
            position + offset
            for position in x_positions
        ]

        values = [
            selected.get(users, 0.0)
            for users in user_values
        ]

        bars = axis.bar(
            bar_positions,
            values,
            width=bar_width,
            label=system_label(system),
        )

        axis.bar_label(
            bars,
            labels=[
                f"{value:.4f}"
                for value in values
            ],
            padding=3,
            fontsize=8,
        )

    axis.set_title(
        "Ergänzende Hochlastreihe: Fehlerrate"
    )
    axis.set_xlabel("Simulierte Locust-User")
    axis.set_ylabel("Fehlerrate in %")
    axis.set_xticks(x_positions)
    axis.set_xticklabels(user_values)
    axis.grid(True, axis="y", alpha=0.3)
    axis.legend()

    maximum = max(
        float(row["fail_rate_percent"])
        for row in rows
    )

    if maximum > 0:
        axis.set_ylim(0, maximum * 1.25)

    figure.tight_layout()

    output_path = (
        plots_dir / "highload_failure_rate.png"
    )

    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    print(f"Gespeichert: {output_path}")

def main() -> None:
    args = parse_args()
    rows = read_rows(args.summary_file)

    args.plots_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plot_metric(
        rows=rows,
        plots_dir=args.plots_dir,
        metric="requests_per_second",
        ylabel="Requests pro Sekunde",
        title="Ergänzende Hochlastreihe: Durchsatz",
        filename="highload_throughput.png",
    )

    plot_metric(
        rows=rows,
        plots_dir=args.plots_dir,
        metric="median_ms",
        ylabel="Antwortzeit in Sekunden",
        title="Ergänzende Hochlastreihe: Median-Latenz",
        filename="highload_median_latency.png",
        divisor=1000.0,
    )

    plot_metric(
        rows=rows,
        plots_dir=args.plots_dir,
        metric="p95_ms",
        ylabel="Antwortzeit in Sekunden",
        title="Ergänzende Hochlastreihe: p95-Latenz",
        filename="highload_p95_latency.png",
        divisor=1000.0,
    )

    plot_metric(
        rows=rows,
        plots_dir=args.plots_dir,
        metric="p99_ms",
        ylabel="Antwortzeit in Sekunden",
        title="Ergänzende Hochlastreihe: p99-Latenz",
        filename="highload_p99_latency.png",
        divisor=1000.0,
    )

    plot_failure_rate(
        rows=rows,
        plots_dir=args.plots_dir,
    )

    print("Hochlastdiagramme erfolgreich erzeugt.")

if __name__ == "__main__":
    main()