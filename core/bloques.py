"""Cálculo de los bloques (períodos) de un turno. Lógica pura, sin BD ni UI."""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BloqueCalculado:
    orden: int
    hora_inicio: str  # 'HH:MM'
    hora_fin: str     # 'HH:MM'


def _a_minutos(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _a_hhmm(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def calcular_bloques(
    hora_inicio: str,
    num_periodos: int,
    duracion_periodo: int,
    recreos: Dict[int, int],
) -> List[BloqueCalculado]:
    """Calcula la hora de inicio y fin de cada período.

    recreos: {despues_de_periodo: duracion_en_minutos}. Ej: {2: 30} = recreo de
    30 min después del período 2.
    """
    for despues in recreos:
        if not 1 <= despues < num_periodos:
            raise ValueError(
                f"El recreo después del período {despues} no es válido "
                f"(debe ser entre 1 y {num_periodos - 1})."
            )

    bloques: List[BloqueCalculado] = []
    reloj = _a_minutos(hora_inicio)
    for orden in range(1, num_periodos + 1):
        inicio = reloj
        reloj += duracion_periodo
        bloques.append(BloqueCalculado(orden, _a_hhmm(inicio), _a_hhmm(reloj)))
        reloj += recreos.get(orden, 0)
    return bloques


def validar_turno(
    hora_fin_turno: str, bloques: List[BloqueCalculado]
) -> Optional[str]:
    """Devuelve un error si los períodos y recreos no caben en el turno."""
    if bloques and _a_minutos(bloques[-1].hora_fin) > _a_minutos(hora_fin_turno):
        return (
            f"Los períodos y recreos terminan a las {bloques[-1].hora_fin}, "
            f"después del fin del turno ({hora_fin_turno}). "
            "Reduzca los períodos, su duración o los recreos."
        )
    return None
