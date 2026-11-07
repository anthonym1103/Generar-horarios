"""Reglas de negocio puras (no dependen de la base de datos ni de la UI)."""
from typing import Iterable, Optional


def capacidad_maxima_horas(bloques_por_turno: Iterable[int], dias_activos: int) -> int:
    """Máximo de horas semanales que cabe en los turnos que trabaja un profesor.

    bloques_por_turno: cantidad de bloques de cada turno que trabaja.
    Ej: solo mañana con 7 bloques y 5 días activos -> 7 * 5 = 35.
        turno completo (7 + 7)                      -> 14 * 5 = 70.
    """
    return sum(bloques_por_turno) * dias_activos


def validar_horas_semanales(horas_semanales: int, capacidad_maxima: int) -> Optional[str]:
    """Devuelve un mensaje de error si las horas no caben en sus turnos, o None si están bien."""
    if capacidad_maxima <= 0:
        return "El profesor no tiene turnos asignados."
    if horas_semanales > capacidad_maxima:
        return (
            f"{horas_semanales} horas semanales no caben en sus turnos "
            f"(máximo {capacidad_maxima}). Amplíe su turno o reduzca sus horas."
        )
    return None