"""Versión B: LCS mediante divide y vencerás (Hirschberg, 1975).

Complejidad: tiempo Θ(m·n) (unas 2·m·n operaciones); memoria Θ(m + n).
"""


def last_row(a: str, a_idx: range, b: str, b_idx: range) -> list[int]:
    """Calcula solo la última fila de la tabla de la DP.

    Recorre los caracteres a[i] para i en a_idx y b[k] para k en b_idx,
    en el orden que indiquen los rangos (hacia delante o hacia atrás).
    row[j] es la longitud de la LCS de esos caracteres de a y los j primeros
    de b. Solo se guardan dos filas a la vez: memoria Θ(len(b_idx)).
    """
    n = len(b_idx)
    previous = [0] * (n + 1)
    for i in a_idx:
        current = [0] * (n + 1)
        for j, k in enumerate(b_idx, start=1):
            if a[i] == b[k]:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current
    return previous


def lcs_hirschberg(a: str, b: str) -> str:
    """Devuelve una subsecuencia común más larga de a y b."""
    chars: list[str] = []

    def solve(a_lo: int, a_hi: int, b_lo: int, b_hi: int) -> None:
        """Añade a chars una LCS de a[a_lo:a_hi] y b[b_lo:b_hi], en orden."""
        # Caso base 1: un tramo vacío no aporta nada.
        if a_lo == a_hi or b_lo == b_hi:
            return

        # Caso base 2: un solo carácter en a. Está en la LCS si aparece
        # en el tramo de b (find busca sin copiar la cadena).
        if a_hi - a_lo == 1:
            if b.find(a[a_lo], b_lo, b_hi) != -1:
                chars.append(a[a_lo])
            return

        # Dividir: partimos a por la mitad.
        mid = (a_lo + a_hi) // 2

        # Pasada hacia delante: mitad izquierda de a con cada prefijo de b.
        forward = last_row(a, range(a_lo, mid), b, range(b_lo, b_hi))
        # Pasada hacia atrás: mitad derecha de a con cada sufijo de b.
        backward = last_row(
            a, range(a_hi - 1, mid - 1, -1), b, range(b_hi - 1, b_lo - 1, -1)
        )

        # Punto de corte de b que maximiza la LCS total:
        # LCS(izquierda, b[:j]) + LCS(derecha, b[j:]).
        n = b_hi - b_lo
        split, best = 0, -1
        for j in range(n + 1):
            total = forward[j] + backward[n - j]
            if total > best:
                split, best = j, total

        # Liberamos las filas antes de las llamadas recursivas; si no, cada
        # nivel de la recursión las mantendría vivas y la memoria crecería.
        del forward, backward

        # Vencer: resolver las dos mitades (primero la izquierda, para que
        # los caracteres queden en orden).
        solve(a_lo, mid, b_lo, b_lo + split)
        solve(mid, a_hi, b_lo + split, b_hi)

    solve(0, len(a), 0, len(b))
    return "".join(chars)