"""Versión A: LCS recursiva directa (sin memorización).

Complejidad: tiempo O(2^(m+n)) en el peor caso; memoria O(m+n) llamadas en la pila.
"""


def lcs_recursive(a: str, b: str) -> str:
    """Devuelve una subsecuencia común más larga de a y b."""

    def solve(i: int, j: int) -> str:
        """Devuelve una LCS de los prefijos a[:i] y b[:j]."""
        # Caso base: si un prefijo está vacío, la LCS es vacía.
        if i == 0 or j == 0:
            return ""

        # Los últimos caracteres coinciden: forman parte de la LCS.
        if a[i - 1] == b[j - 1]:
            return solve(i - 1, j - 1) + a[i - 1]

        # No coinciden: se prueban las dos opciones y se queda la más larga.
        # Sin memorización, los mismos subproblemas se recalculan muchas veces.
        up = solve(i - 1, j)
        left = solve(i, j - 1)
        return up if len(up) >= len(left) else left

    return solve(len(a), len(b))