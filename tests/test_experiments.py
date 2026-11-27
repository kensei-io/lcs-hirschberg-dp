"""Tests del generador, la medición y el flujo completo de experimentos."""

from lcs_hirschberg_dp.dp import lcs_dp
from lcs_hirschberg_dp.experiments import Series, run_series, save_csv
from lcs_hirschberg_dp.generator import ALPHABETS, make_pair
from lcs_hirschberg_dp.measure import measure, run_isolated
from lcs_hirschberg_dp.plots import plot_all


def test_make_pair_is_reproducible():
    assert make_pair(100, "ACGT", seed=1) == make_pair(100, "ACGT", seed=1)


def test_make_pair_changes_with_seed():
    assert make_pair(100, "ACGT", seed=1) != make_pair(100, "ACGT", seed=2)


def test_make_pair_length_and_alphabet():
    for alphabet in ALPHABETS.values():
        a, b = make_pair(50, alphabet)
        assert len(a) == len(b) == 50
        assert set(a) <= set(alphabet)
        assert set(b) <= set(alphabet)


def test_measure_returns_consistent_results():
    m = measure("C", 50, repeats=2)
    a, b = make_pair(50)
    assert not m.timed_out
    assert m.lcs_length == len(lcs_dp(a, b))
    assert m.cpu_time_s is not None and m.cpu_time_s >= 0
    assert m.peak_memory_bytes is not None and m.peak_memory_bytes > 0


def test_timeout_stops_slow_runs():
    # La versión A con 40 símbolos sin coincidencias tardaría años.
    assert run_isolated("A", "time", 40, "AB", 0, timeout=0.5) is None


def test_experiment_pipeline_writes_csv_and_figures(tmp_path):
    # Versión en miniatura de los experimentos completos.
    series_list = (
        Series("small", ("A", "B", "C"), (4, 6), (4,), 10.0),
        Series("large", ("B", "C"), (20, 40), (4,), 10.0),
        Series("alphabet", ("A", "B", "C"), (6,), (2, 26), 10.0),
    )
    rows = []
    for series in series_list:
        rows.extend(run_series(series, repeats=1, seed=0))
    assert len(rows) == 6 + 4 + 6

    csv_path = tmp_path / "measurements.csv"
    save_csv(rows, csv_path)
    figures = plot_all(csv_path, tmp_path)
    assert [f.name for f in figures] == ["time.png", "memory.png", "alphabet.png"]
    assert all(f.stat().st_size > 0 for f in figures)