"""Gráficas de los resultados a partir del CSV de mediciones."""

import csv
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

# Un color y un marcador fijos por versión (el marcador permite distinguirlas
# también en blanco y negro o con daltonismo).
STYLE = {
    "A": {"color": "#257de0", "marker": "o", "label": "A · recursiva"},
    "B": {"color": "#f47230", "marker": "s", "label": "B · Hirschberg"},
    "C": {"color": "#00b894", "marker": "^", "label": "C · DP tabular"},
}
GRAY = "#666666"


def load_rows(csv_path: Path) -> list[dict]:
    """Lee el CSV y convierte cada columna a su tipo."""
    rows = []
    with csv_path.open(encoding="utf-8") as file:
        for raw in csv.DictReader(file):
            rows.append(
                {
                    "series": raw["series"],
                    "algorithm": raw["algorithm"],
                    "alphabet_size": int(raw["alphabet_size"]),
                    "length": int(raw["length"]),
                    "cpu_time_s": float(raw["cpu_time_s"] or "nan"),
                    # En bytes, para que las marcas del eje caigan en valores redondos.
                    "peak_memory_bytes": float(raw["peak_memory_kib"] or "nan") * 1024,
                    "timed_out": raw["timed_out"] == "True",
                }
            )
    return rows


def _style_axes(ax: Axes, title: str, xlabel: str, ylabel: str) -> None:
    """Aspecto común: título, ejes discretos y rejilla suave."""
    ax.set_title(title, fontsize=11, loc="left")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="major", color="#dddddd", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def _plot_series(ax: Axes, rows: list[dict], series: str, field: str) -> None:
    """Dibuja una línea por versión para una serie y una magnitud."""
    lengths = sorted({r["length"] for r in rows if r["series"] == series})
    for algorithm, style in STYLE.items():
        selected = [
            r for r in rows if r["series"] == series and r["algorithm"] == algorithm
        ]
        points = sorted((r["length"], r[field]) for r in selected if not r["timed_out"])
        if not points:
            continue
        label = style["label"]
        # Versiones cortadas por el límite de tiempo: se indica en la leyenda.
        cut = [r["length"] for r in selected if r["timed_out"]]
        if cut:
            label += f" (límite superado en n = {cut[0]})"
        xs, ys = zip(*points, strict=True)
        ax.plot(
            xs,
            ys,
            color=style["color"],
            marker=style["marker"],
            label=label,
            linewidth=2,
            markersize=6,
        )
    # Marcas del eje x solo en las longitudes medidas.
    ax.set_xticks(lengths, [str(n) for n in lengths])
    ax.minorticks_off()


def _reference(
    ax: Axes, rows: list[dict], series: str, field: str, algorithm: str, power: int
) -> None:
    """Línea discontinua proporcional a n^power, anclada al primer punto de una versión."""
    points = sorted(
        (r["length"], r[field])
        for r in rows
        if r["series"] == series and r["algorithm"] == algorithm and not r["timed_out"]
    )
    if not points:
        return
    x0, y0 = points[0]
    xs = [x for x, _ in points]
    ax.plot(
        xs,
        [y0 * (x / x0) ** power for x in xs],
        linestyle="--" if power == 2 else ":",
        linewidth=1.2,
        color=GRAY,
        label="referencia ∝ n²" if power == 2 else "referencia ∝ n",
    )


def format_seconds(value: float) -> str:
    """Tiempo con la unidad adecuada: 50 µs, 2 ms, 1.5 s…"""
    if value == 0:
        return "0"
    if value >= 1:
        return f"{value:g} s"
    if value >= 1e-3:
        return f"{value * 1e3:g} ms"
    return f"{value * 1e6:g} µs"


def format_bytes(value: float) -> str:
    """Memoria con la unidad adecuada (sistema decimal): 500 B, 20 kB, 50 MB…"""
    if value >= 1e6:
        return f"{value / 1e6:g} MB"
    if value >= 1e3:
        return f"{value / 1e3:g} kB"
    return f"{value:g} B"


def _log_y(ax: Axes, formatter) -> None:
    """Eje y logarítmico con marcas en 1, 2, 5, 10, 20, 50… y unidades legibles."""
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: formatter(v)))
    ax.yaxis.set_minor_formatter(NullFormatter())


def plot_metric(rows: list[dict], field: str, ylabel: str, path: Path) -> Path:
    """Figura con la serie pequeña (izquierda) y la grande (derecha)."""
    formatter = format_seconds if field == "cpu_time_s" else format_bytes
    fig = Figure(figsize=(10, 4.2), layout="constrained")
    left, right = fig.subplots(1, 2)

    _plot_series(left, rows, "small", field)
    _log_y(left, formatter)
    _style_axes(left, "Serie pequeña (A, B, C)", "longitud n de cada cadena", ylabel)
    left.legend(frameon=False, fontsize=8)

    right.set_xscale("log")
    _plot_series(right, rows, "large", field)
    _reference(right, rows, "large", field, "C", power=2)
    if field == "peak_memory_bytes":
        # La memoria de Hirschberg debería crecer de forma lineal.
        _reference(right, rows, "large", field, "B", power=1)
    _log_y(right, formatter)
    _style_axes(right, "Serie grande (B, C) · escala log-log", "longitud n", ylabel)
    right.legend(frameon=False, fontsize=8)

    fig.savefig(path, dpi=200)
    return path


def plot_alphabet(rows: list[dict], path: Path) -> Path:
    """Tiempo según el tamaño del alfabeto (longitud fija)."""
    fig = Figure(figsize=(10, 4), layout="constrained")
    axes = fig.subplots(1, 2)
    groups = (("A",), ("B", "C"))

    for ax, algorithms in zip(axes, groups, strict=True):
        data = [
            r
            for r in rows
            if r["series"] == "alphabet" and r["algorithm"] in algorithms
        ]
        if not data:
            ax.set_visible(False)
            continue
        sizes = sorted({r["alphabet_size"] for r in data})
        width = 0.8 / len(algorithms)
        for k, algorithm in enumerate(algorithms):
            values = {
                r["alphabet_size"]: r["cpu_time_s"]
                for r in data
                if r["algorithm"] == algorithm
            }
            positions = [
                i + (k - (len(algorithms) - 1) / 2) * width for i in range(len(sizes))
            ]
            bars = ax.bar(
                positions,
                [values.get(s, float("nan")) for s in sizes],
                width=width * 0.92,
                color=STYLE[algorithm]["color"],
                label=STYLE[algorithm]["label"],
            )
            ax.bar_label(
                bars,
                labels=[format_seconds(float(f"{b.get_height():.3g}")) for b in bars],
                fontsize=8,
                color=GRAY,
                padding=2,
            )
        ax.set_xticks(range(len(sizes)), [f"{s} símbolos" for s in sizes])
        n = data[0]["length"]
        name = "Versión" if len(algorithms) == 1 else "Versiones"
        title = f"{name} {' y '.join(algorithms)} · n = {n}"
        _style_axes(ax, title, "alfabeto", "tiempo de CPU")
        ax.grid(False, axis="x")
        if len(algorithms) == 1:
            # Los tiempos de A varían en órdenes de magnitud: escala logarítmica.
            _log_y(ax, format_seconds)
        else:
            # Margen arriba para que la leyenda no tape las etiquetas.
            ax.set_ylim(top=ax.get_ylim()[1] * 1.25)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: format_seconds(v)))
            ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=2)

    fig.savefig(path, dpi=200)
    return path


def plot_all(csv_path: Path, out_dir: Path) -> list[Path]:
    """Genera todas las gráficas y devuelve sus rutas."""
    rows = load_rows(csv_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    return [
        plot_metric(rows, "cpu_time_s", "tiempo de CPU", out_dir / "time.png"),
        plot_metric(
            rows, "peak_memory_bytes", "memoria máxima", out_dir / "memory.png"
        ),
        plot_alphabet(rows, out_dir / "alphabet.png"),
    ]