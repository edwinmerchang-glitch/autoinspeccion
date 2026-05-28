"""
db/connection.py
----------------
Centraliza la conexión a SQLite. Usa un context manager para garantizar
que cada conexión se cierre correctamente, eliminando los c.close() manuales.

Uso:
    from db.connection import get_db

    with get_db() as conn:
        df = pd.read_sql("SELECT * FROM tiendas", conn)
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "autoinspection.db"


def _raw_connection() -> sqlite3.Connection:
    """Conexión base con row_factory habilitado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Compatibilidad con código legado que importa get_connection desde init_db
def get_connection() -> sqlite3.Connection:
    """Retorna una conexión sin cerrar. Preferir get_db() cuando sea posible."""
    return _raw_connection()


@contextmanager
def get_db():
    """
    Context manager recomendado.

    with get_db() as conn:
        conn.execute(...)      # auto-commit + close al salir
    """
    conn = _raw_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
