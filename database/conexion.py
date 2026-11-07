"""Manejo de la conexión a SQLite."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from config import DATA_DIR, DB_PATH
from database.esquema import DIAS_INICIALES, ESQUEMA_SQL


def obtener_conexion(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Abre una conexión con las foreign keys activadas.

    SQLite las trae desactivadas por defecto, por eso el PRAGMA es obligatorio
    en cada conexión nueva.
    """
    ruta = Path(db_path) if db_path else DB_PATH
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(ruta)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # permite acceder por nombre: fila["nombre"]
    return conn


@contextmanager
def conexion(db_path: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    """Context manager: hace commit si todo sale bien, rollback si hay error."""
    conn = obtener_conexion(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_bd(db_path: Optional[Path] = None) -> None:
    """Crea las tablas (si no existen) y carga los datos fijos (días)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with conexion(db_path) as conn:
        conn.executescript(ESQUEMA_SQL)
        conn.executemany(
            "INSERT OR IGNORE INTO dia (nombre, activo) VALUES (?, ?)",
            DIAS_INICIALES,
        )