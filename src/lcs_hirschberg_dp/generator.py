"""Generación reproducible de parejas de cadenas para los experimentos."""

import random
import string

# Alfabetos disponibles, identificados por su tamaño.
ALPHABETS = {
    2: "AB",
    4: "ACGT",
    26: string.ascii_uppercase,
}


def make_pair(length: int, alphabet: str = "ACGT", seed: int = 0) -> tuple[str, str]:
    """Devuelve una pareja de cadenas aleatorias de la misma longitud.

    La pareja depende solo de (seed, length, alphabet): cualquier proceso que
    la pida con los mismos parámetros obtiene exactamente las mismas cadenas.
    """
    # Una semilla de texto es determinista entre ejecuciones (a diferencia
    # de hash()), así cada tamaño tiene su propia secuencia reproducible.
    rng = random.Random(f"{seed}:{length}:{alphabet}")
    a = "".join(rng.choices(alphabet, k=length))
    b = "".join(rng.choices(alphabet, k=length))
    return a, b