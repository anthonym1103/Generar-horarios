"""Configuración global del proyecto.
 
Las rutas funcionan tanto ejecutando desde código fuente como cuando
la app está empaquetada como .exe con PyInstaller.
"""
import sys
from pathlib import Path
 
 
def _directorio_base() -> Path:
    # Empaquetado con PyInstaller: la BD debe vivir junto al .exe,
    # no dentro de la carpeta temporal donde se descomprime la app.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent
 
 
BASE_DIR = _directorio_base()
DATA_DIR = BASE_DIR / "datos"
DB_PATH = DATA_DIR / "liceo.db"
 