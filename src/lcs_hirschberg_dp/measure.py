"""Medición de tiempo de CPU y memoria máxima de cada versión.

Cada medición se ejecuta en un proceso independiente:
- una medición no contamina a la siguiente (memoria, cachés, recolector);
- se puede cortar una ejecución que supere el límite de tiempo.
"""

import multiprocessing as mp
import statistics
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing.connection import Connection

from lcs_hirschberg_dp.dp import lcs_dp
from lcs_hirschberg_dp.generator import make_pair
from lcs_hirschberg_dp.hirschberg import lcs_hirschberg
from lcs_hirschberg_dp.recursive import lcs_recursive

ALGORITHMS: dict[str, Callable[[str, str], str]] = {
    "A": lcs_recursive,
    "B": lcs_hirschberg,
    "C": lcs_dp,
}


@dataclass
class Measurement:
    """Resultado de medir una versión con una pareja de cadenas."""

    algorithm: str
    length: int
    alphabet: str
    lcs_length: int | None  # None si se superó el límite de tiempo
    cpu_time_s: float | None  # mediana de las repeticiones
    peak_memory_bytes: int | None
    timed_out: bool


def _worker(
    algorithm: str, mode: str, length: int, alphabet: str, seed: int, conn: Connection
) -> None:
    """Se ejecuta en el proceso hijo: genera la pareja, mide y envía el resultado."""
    a, b = make_pair(length, alphabet, seed)
    func = ALGORITHMS[algorithm]

    if mode == "time":
        # Tiempo de CPU del proceso (no incluye esperas ni otros programas).
        start = time.process_time()
        result = func(a, b)
        value: float = time.process_time() - start
    else:
        # Pico de memoria reservada por el algoritmo. Las cadenas de entrada
        # se generan antes de empezar a medir, así que no cuentan.
        tracemalloc.start()
        result = func(a, b)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        value = peak

    conn.send((value, len(result)))
    conn.close()


def run_isolated(
    algorithm: str, mode: str, length: int, alphabet: str, seed: int, timeout: float
) -> tuple[float, int] | None:
    """Ejecuta una medición en un proceso nuevo.

    Devuelve (valor, longitud de la LCS), o None si se supera el límite de tiempo.
    """
    ctx = mp.get_context("spawn")  # proceso limpio, igual en macOS, Linux y Windows
    receiver, sender = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_worker, args=(algorithm, mode, length, alphabet, seed, sender)
    )
    process.start()
    sender.close()  # el padre solo recibe

    if receiver.poll(timeout):
        try:
            value, lcs_length = receiver.recv()
        except EOFError:
            # El hijo terminó sin enviar nada: hubo un error dentro de él.
            process.join()
            msg = f"La medición falló en el proceso hijo (código {process.exitcode})"
            raise RuntimeError(msg) from None
        process.join()
        return value, lcs_length

    # Límite superado: se detiene el proceso hijo.
    process.terminate()
    process.join()
    return None


def measure(
    algorithm: str,
    length: int,
    alphabet: str = "ACGT",
    seed: int = 0,
    repeats: int = 5,
    timeout: float = 60.0,
) -> Measurement:
    """Mide una versión: mediana de `repeats` tiempos y una medición de memoria.

    El tiempo y la memoria se miden en ejecuciones separadas, porque tracemalloc
    ralentiza el programa y falsearía los tiempos.
    """
    times: list[float] = []
    lcs_length = None
    for _ in range(repeats):
        outcome = run_isolated(algorithm, "time", length, alphabet, seed, timeout)
        if outcome is None:
            # Límite superado: no tiene sentido seguir repitiendo.
            return Measurement(
                algorithm=algorithm,
                length=length,
                alphabet=alphabet,
                lcs_length=None,
                cpu_time_s=None,
                peak_memory_bytes=None,
                timed_out=True,
            )
        cpu_time, lcs_length = outcome
        times.append(cpu_time)

    # Con la misma entrada, el pico de memoria es determinista: basta una medición.
    outcome = run_isolated(algorithm, "memory", length, alphabet, seed, timeout)
    if outcome is None:
        # Con tracemalloc activo el programa va más lento y puede superar el
        # límite aunque la medición de tiempo sí terminara: se conserva el tiempo.
        return Measurement(
            algorithm=algorithm,
            length=length,
            alphabet=alphabet,
            lcs_length=lcs_length,
            cpu_time_s=statistics.median(times),
            peak_memory_bytes=None,
            timed_out=True,
        )
    peak, _ = outcome

    return Measurement(
        algorithm=algorithm,
        length=length,
        alphabet=alphabet,
        lcs_length=lcs_length,
        cpu_time_s=statistics.median(times),
        peak_memory_bytes=int(peak),
        timed_out=False,
    )