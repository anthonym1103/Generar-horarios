"""Entidades del dominio como dataclasses simples.

1 hora = 1 hora académica = 1 período = 1 Bloque.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Turno:
    nombre: str
    hora_inicio: str       # 'HH:MM'
    hora_fin: str          # 'HH:MM'
    num_periodos: int
    duracion_periodo: int  # minutos
    id: Optional[int] = None


@dataclass
class Recreo:
    turno_id: int
    despues_de_periodo: int
    duracion: int  # minutos
    id: Optional[int] = None


@dataclass
class Anio:
    nombre: str
    id: Optional[int] = None


@dataclass
class AnioTurno:
    anio_id: int
    turno_id: int
    id: Optional[int] = None


@dataclass
class Seccion:
    letra: str
    id: Optional[int] = None


@dataclass
class AnioCurso:
    anio_id: int
    seccion_id: int
    id: Optional[int] = None


@dataclass
class AnioCursoTurno:
    """Excepción: turno propio de una sección distinto al de su año."""
    anio_curso_id: int
    turno_id: int
    id: Optional[int] = None


@dataclass
class Asignatura:
    anio_id: int
    nombre: str
    bloques_semanales: int
    bloques_consecutivos: int = 2
    id: Optional[int] = None

    @property
    def sesiones_por_semana(self) -> int:
        """Cuántas veces a la semana se dicta (cada sesión = N bloques seguidos)."""
        return self.bloques_semanales // self.bloques_consecutivos


@dataclass
class Profesor:
    nombre: str
    apellido: str
    horas_semanales: int
    id: Optional[int] = None

    @property
    def nombre_completo(self) -> str:
        return f"{self.apellido} {self.nombre}"


@dataclass
class ProfesorTurno:
    profesor_id: int
    turno_id: int
    id: Optional[int] = None


@dataclass
class ProfesorAsignatura:
    profesor_id: int
    asignatura_id: int
    id: Optional[int] = None


@dataclass
class Dia:
    nombre: str
    activo: bool = True
    id: Optional[int] = None


@dataclass
class Bloque:
    turno_id: int
    orden: int
    hora_inicio: str  # 'HH:MM'
    hora_fin: str     # 'HH:MM'
    id: Optional[int] = None


@dataclass
class CargaAcademica:
    anio_curso_id: int
    asignatura_id: int
    bloques_semanales: int
    bloques_consecutivos: int = 2
    profesor_id: Optional[int] = None  # None = aún sin asignar (lo decide el generador)
    profesor_fijo: bool = False        # True = el generador debe respetar profesor_id
    id: Optional[int] = None

    @property
    def sesiones_por_semana(self) -> int:
        """Cuántas veces a la semana se dicta (cada sesión = N bloques seguidos)."""
        return self.bloques_semanales // self.bloques_consecutivos


@dataclass
class Horario:
    anio_curso_id: int
    dia_id: int
    bloque_id: int
    asignatura_id: int
    profesor_id: int
    id: Optional[int] = None