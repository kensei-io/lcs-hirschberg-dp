"""Tests de corrección para las versiones de LCS."""

import pytest

from lcs_hirschberg_dp.dp import build_table, lcs_dp

# Cuando tengamos las versiones A y B, solo habrá que añadirlas aquí.
IMPLEMENTATIONS = [lcs_dp]


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