"""Tests de corrección para las versiones de LCS."""

import random

import pytest

from lcs_hirschberg_dp.dp import build_table, lcs_dp
from lcs_hirschberg_dp.recursive import lcs_recursive

# Cuando tengamos la versión B, solo habrá que añadirla aquí.
IMPLEMENTATIONS = [lcs_dp, lcs_recursive]


def is_subsequence(sub: str, s: str) -> bool:
    """Comprueba si sub es subsecuencia de s (en orden, no necesariamente contigua)."""
    it = iter(s)
    return all(char in it for char in sub)


# (a, b, longitud esperada de la LCS)
CASES = [
    ("", "", 0),
    ("", "ABC", 0),
    ("ABC", "", 0),
    ("A", "A", 1),
    ("A", "B", 0),
    ("ABC", "ABC", 3),
    ("ABC", "DEF", 0),
    ("ACB", "AB", 2),
    ("AGGTAB", "GXTXAYB", 4),
    ("ABCBDAB", "BDCABA", 4),
]


@pytest.mark.parametrize("lcs", IMPLEMENTATIONS)
@pytest.mark.parametrize(("a", "b", "expected"), CASES)
def test_lcs_length_and_validity(lcs, a, b, expected):
    result = lcs(a, b)
    assert len(result) == expected
    assert is_subsequence(result, a)
    assert is_subsequence(result, b)


def test_table_small_example():
    # El ejemplo hecho a mano: a = "ACB", b = "AB"
    assert build_table("ACB", "AB") == [
        [0, 0, 0],
        [0, 1, 1],
        [0, 1, 1],
        [0, 1, 2],
    ]


@pytest.mark.parametrize("lcs", IMPLEMENTATIONS)
def test_random_pairs_match_reference(lcs):
    # Compara cada versión con la DP (referencia) en 200 parejas aleatorias.
    # La semilla fija hace que las parejas sean siempre las mismas.
    rng = random.Random(42)
    for _ in range(200):
        a = "".join(rng.choices("ACGT", k=rng.randint(0, 9)))
        b = "".join(rng.choices("ACGT", k=rng.randint(0, 9)))
        result = lcs(a, b)
        assert len(result) == len(lcs_dp(a, b))
        assert is_subsequence(result, a)
        assert is_subsequence(result, b)