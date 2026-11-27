"""Experimentos: ejecuta las series de medidas, guarda el CSV y dibuja las gráficas.

Uso:
    uv run lcs-hirschberg-dp               # experimentos completos
    uv run lcs-hirschberg-dp --quick       # versión reducida para comprobar
    uv run lcs-hirschberg-dp --plots-only  # rehacer las gráficas desde el CSV
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from lcs_hirschberg_dp.generator import ALPHABETS
from lcs_hirschberg_dp.measure import measure

CSV_FIELDS = [
    "series",
    "algorithm",
    "alphabet_size",
    "length",
    "lcs_length",
    "cpu_time_s",
    "peak_memory_kib",
    "timed_out",
]


@dataclass(frozen=True)
class Series:
    """Una serie de experimentos: qué versiones, con qué longitudes y alfabetos."""

    name: str
    algorithms: tuple[str, ...]
    lengths: tuple[int, ...]
    alphabet_sizes: tuple[int, ...]
    timeout: float  # segundos por ejecución


# Experimentos completos (los de la memoria).
FULL_SERIES = (
    # Serie pequeña: las tres versiones; A se corta al superar el límite.
    Series("small", ("A", "B", "C"), tuple(range(4, 25, 2)), (4,), 20.0),
    # Serie grande: solo B y C (A tardaría años).
    Series("large", ("B", "C"), (250, 500, 1000, 2000, 4000), (4,), 600.0),
    # Influencia del tamaño del alfabeto, con longitud fija.
    Series("alphabet", ("A",), (14,), (2, 4, 26), 60.0),
    Series("alphabet", ("B", "C"), (1000,), (2, 4, 26), 600.0),
)

# Versión reducida: comprueba que todo funciona en menos de un minuto.
QUICK_SERIES = (
    Series("small", ("A", "B", "C"), (4, 6, 8, 10), (4,), 10.0),
    Series("large", ("B", "C"), (100, 200, 400), (4,), 60.0),
    Series("alphabet", ("A",), (8,), (2, 4, 26), 10.0),
    Series("alphabet", ("B", "C"), (200,), (2, 4, 26), 60.0),
)


def run_series(series: Series, repeats: int, seed: int) -> list[dict]:
    """Ejecuta una serie y devuelve una fila (diccionario) por medición."""
    rows = []
    for size in series.alphabet_sizes:
        alphabet = ALPHABETS[size]
        for algorithm in series.algorithms:
            for length in series.lengths:
                m = measure(algorithm, length, alphabet, seed, repeats, series.timeout)
                rows.append(
                    {
                        "series": series.name,
                        "algorithm": algorithm,
                        "alphabet_size": size,
                        "length": length,
                        "lcs_length": m.lcs_length,
                        "cpu_time_s": m.cpu_time_s,
                        "peak_memory_kib": (
                            None
                            if m.peak_memory_bytes is None
                            else m.peak_memory_bytes / 1024
                        ),
                        "timed_out": m.timed_out,
                    }
                )
                print(_describe(rows[-1]), flush=True)
                if m.timed_out:
                    # Si una longitud supera el límite, las mayores también lo harán.
                    break
    return rows


def _describe(row: dict) -> str:
    """Texto de una línea para seguir el progreso en la terminal."""
    head = (
        f"[{row['series']:<8}] {row['algorithm']}  "
        f"alfabeto={row['alphabet_size']:<2}  n={row['length']:<5}"
    )
    if row["cpu_time_s"] is None:
        return f"{head}  límite de tiempo superado"
    memory = (
        "límite superado"
        if row["peak_memory_kib"] is None
        else f"{row['peak_memory_kib']:10.1f} KiB"
    )
    return f"{head}  {row['cpu_time_s']:9.4f} s  {memory}  LCS={row['lcs_length']}"


def save_csv(rows: list[dict], path: Path) -> None:
    """Guarda las mediciones en un CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Punto de entrada del comando lcs-hirschberg-dp."""
    parser = argparse.ArgumentParser(description="Experimentos de LCS (A, B y C).")
    parser.add_argument(
        "--quick", action="store_true", help="versión reducida para comprobar"
    )
    parser.add_argument(
        "--plots-only", action="store_true", help="solo rehacer las gráficas"
    )
    parser.add_argument("--repeats", type=int, default=5, help="repeticiones (5)")
    parser.add_argument("--seed", type=int, default=0, help="semilla base (0)")
    args = parser.parse_args()

    out_dir = Path("results/quick") if args.quick else Path("results")
    csv_path = out_dir / "measurements.csv"

    if not args.plots_only:
        series_list = QUICK_SERIES if args.quick else FULL_SERIES
        repeats = 1 if args.quick else args.repeats
        rows = []
        for series in series_list:
            rows.extend(run_series(series, repeats, args.seed))
        save_csv(rows, csv_path)
        print(f"\nMediciones guardadas en {csv_path}")

    # Se importa aquí para que los procesos de medición no carguen matplotlib.
    from lcs_hirschberg_dp.plots import plot_all

    for figure in plot_all(csv_path, out_dir):
        print(f"Gráfica guardada en {figure}")


if __name__ == "__main__":
    main()