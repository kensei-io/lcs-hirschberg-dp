"""Tests del generador de cadenas y del módulo de medición."""

from lcs_hirschberg_dp.dp import lcs_dp
from lcs_hirschberg_dp.generator import ALPHABETS, make_pair
from lcs_hirschberg_dp.measure import measure, run_isolated


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