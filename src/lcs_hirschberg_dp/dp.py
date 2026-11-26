"""Versión C: LCS mediante programación dinámica tabular.

Complejidad: tiempo Θ(m·n), memoria Θ(m·n).
"""


def build_table(a: str, b: str) -> list[list[int]]:
    """Construye la tabla L de tamaño (m+1) x (n+1).

    L[i][j] es la longitud de la LCS de a[:i] y b[:j].
    """
    m, n = len(a), len(b)
    # Tabla de ceros: cada fila es una lista independiente.
    table = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                # Los caracteres coinciden: forman parte de la LCS.
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                # No coinciden: la mejor opción descartando uno de los dos.
                table[i][j] = max(table[i - 1][j], table[i][j - 1])

    return table


def reconstruct(table: list[list[int]], a: str, b: str) -> str:
    """Recorre la tabla desde L[m][n] hasta el borde y devuelve una LCS."""
    i, j = len(a), len(b)
    chars: list[str] = []

    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            # Coincidencia: el carácter es de la LCS; avanzamos en diagonal.
            chars.append(a[i - 1])
            i -= 1
            j -= 1
        elif table[i - 1][j] >= table[i][j - 1]:
            # Arriba es mejor o igual: subimos (criterio fijo en empates).
            i -= 1
        else:
            # Izquierda es mejor.
            j -= 1

    # Los caracteres se han recogido de atrás hacia delante.
    return "".join(reversed(chars))


def lcs_dp(a: str, b: str) -> str:
    """Devuelve una subsecuencia común más larga de a y b."""
    return reconstruct(build_table(a, b), a, b)