"""Acceso a datos de turnos, recreos y bloques."""
import sqlite3
from typing import Dict, Optional

from core.bloques import calcular_bloques, validar_turno


def crear_turno(
    conn: sqlite3.Connection,
    nombre: str,
    hora_inicio: str,
    hora_fin: str,
    num_periodos: int,
    duracion_periodo: int,
    recreos: Optional[Dict[int, int]] = None,
) -> int:
    """Crea un turno con sus recreos y genera automáticamente sus bloques.

    Lanza ValueError si los períodos y recreos no caben dentro del turno.
    """
    recreos = recreos or {}
    if len(recreos) > 1:
        raise ValueError("Cada turno admite un solo recreo.")
    bloques = calcular_bloques(hora_inicio, num_periodos, duracion_periodo, recreos)
    error = validar_turno(hora_fin, bloques)
    if error:
        raise ValueError(error)

    cur = conn.execute(
        "INSERT INTO turno (nombre, hora_inicio, hora_fin, num_periodos, duracion_periodo) "
        "VALUES (?, ?, ?, ?, ?)",
        (nombre, hora_inicio, hora_fin, num_periodos, duracion_periodo),
    )
    turno_id = cur.lastrowid
    conn.executemany(
        "INSERT INTO recreo (turno_id, despues_de_periodo, duracion) VALUES (?, ?, ?)",
        [(turno_id, despues, dur) for despues, dur in recreos.items()],
    )
    conn.executemany(
        "INSERT INTO bloque (turno_id, orden, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)",
        [(turno_id, b.orden, b.hora_inicio, b.hora_fin) for b in bloques],
    )
    return turno_id