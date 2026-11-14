"""Agrupación de exposiciones en visitas (gap < 1 día). Origen: poc/02_fetch_cutouts.py::group_visits."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def group_visits[T](items: Iterable[T], key: Callable[[T], float], gap_days: float = 1.0) -> list[list[T]]:
    """Agrupa elementos ordenados por tiempo: un gap > gap_days abre una visita nueva."""
    visits: list[list[T]] = []
    cur: list[T] = []
    last: float | None = None
    for it in sorted(items, key=key):
        t = key(it)
        if last is not None and t - last > gap_days:
            visits.append(cur)
            cur = []
        cur.append(it)
        last = t
    if cur:
        visits.append(cur)
    return visits
