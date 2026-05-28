"""
db/queries.py
-------------
Todas las consultas SQL en un solo lugar. Cada función recibe los parámetros
necesarios y retorna un DataFrame o un valor escalar.

Beneficios:
- Un solo lugar para cambiar nombres de tablas/columnas.
- Fácil de testear de forma aislada.
- Las páginas solo llaman funciones con nombres descriptivos.
"""

import pandas as pd
from db.connection import get_db, get_connection


# ── Tiendas ────────────────────────────────────────────────────────────────────

def get_tiendas() -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql("SELECT id, nombre FROM tiendas ORDER BY id", conn)


# ── Auditorías ─────────────────────────────────────────────────────────────────

def get_auditorias(tienda_id: str) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql(
            """SELECT id, fecha, auditor, calificacion_global, resultado
               FROM auditorias
               WHERE tienda_id = ?
               ORDER BY fecha DESC""",
            conn, params=(tienda_id,)
        )


def get_auditoria(auditoria_id: int) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM auditorias WHERE id = ?", (auditoria_id,)
        ).fetchone()
        return dict(row) if row else {}


def create_auditoria(tienda_id: str, fecha: str, auditor: str, resultado: str) -> int:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO auditorias (tienda_id, fecha, auditor, calificacion_global, resultado)
               VALUES (?, ?, ?, 0.0, ?)""",
            (tienda_id, fecha, auditor, resultado)
        )
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def update_calificacion_global(auditoria_id: int, valor: float) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE auditorias SET calificacion_global = ? WHERE id = ?",
            (valor, auditoria_id)
        )


def update_resultado(auditoria_id: int, resultado: str) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE auditorias SET resultado = ? WHERE id = ?",
            (resultado, auditoria_id)
        )


# ── Items Farma ────────────────────────────────────────────────────────────────

def get_items_farma(auditoria_id: int) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql(
            """SELECT if.*, sf.nombre AS seccion_nombre
               FROM items_farma if
               JOIN secciones_farma sf ON sf.id = if.seccion_id
               WHERE if.auditoria_id = ?
               ORDER BY if.seccion_id, if.id""",
            conn, params=(auditoria_id,)
        )


def update_item_farma_puntaje(item_id: int, puntaje: int) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE items_farma SET puntaje = ? WHERE id = ?",
            (puntaje, item_id)
        )


def update_item_farma_observacion(item_id: int, observacion: str | None) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE items_farma SET observacion = ? WHERE id = ?",
            (observacion, item_id)
        )


def copy_farma_template(new_id: int, template_id: int = 1) -> None:
    """Copia los ítems farma de una auditoría plantilla a una nueva."""
    with get_db() as conn:
        template = conn.execute(
            "SELECT * FROM items_farma WHERE auditoria_id = ?", (template_id,)
        ).fetchall()
        for item in template:
            conn.execute(
                """INSERT INTO items_farma (auditoria_id, seccion_id, item, puntaje, observacion)
                   VALUES (?, ?, ?, 0, NULL)""",
                (new_id, item["seccion_id"], item["item"])
            )


# ── Items Tienda ───────────────────────────────────────────────────────────────

def get_items_tienda(auditoria_id: int) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql(
            "SELECT * FROM items_tienda WHERE auditoria_id = ?",
            conn, params=(auditoria_id,)
        )


def update_calificacion_tienda(item_id: int, calificacion: float) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE items_tienda SET calificacion = ? WHERE id = ?",
            (calificacion, item_id)
        )


def copy_tienda_template(new_id: int, template_id: int = 1) -> None:
    with get_db() as conn:
        template = conn.execute(
            "SELECT * FROM items_tienda WHERE auditoria_id = ?", (template_id,)
        ).fetchall()
        for it in template:
            conn.execute(
                """INSERT INTO items_tienda (auditoria_id, criterio, minimo, superior, meta, calificacion)
                   VALUES (?, ?, ?, ?, ?, 0)""",
                (new_id, it["criterio"], it["minimo"], it["superior"], it["meta"])
            )


# ── Hallazgos ──────────────────────────────────────────────────────────────────

def get_hallazgos(auditoria_id: int) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql(
            "SELECT * FROM hallazgos WHERE auditoria_id = ? ORDER BY id",
            conn, params=(auditoria_id,)
        )


def create_hallazgo(auditoria_id: int, proceso: str, descripcion: str, observaciones: str | None) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO hallazgos (auditoria_id, proceso_afectado, hallazgo, observaciones, estado)
               VALUES (?, ?, ?, ?, 'Pendiente')""",
            (auditoria_id, proceso, descripcion, observaciones)
        )


def update_hallazgo(hid: int, proceso: str, descripcion: str, observaciones: str | None, estado: str) -> None:
    with get_db() as conn:
        conn.execute(
            """UPDATE hallazgos
               SET proceso_afectado = ?, hallazgo = ?, observaciones = ?, estado = ?
               WHERE id = ?""",
            (proceso, descripcion, observaciones, estado, hid)
        )


def set_hallazgo_estado(hid: int, estado: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE hallazgos SET estado = ? WHERE id = ?", (estado, hid))


def delete_hallazgo(hid: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM hallazgos WHERE id = ?", (hid,))


def bulk_create_hallazgos(auditoria_id: int, hallazgos: list[tuple]) -> None:
    """hallazgos: lista de (proceso, descripcion, observaciones)"""
    with get_db() as conn:
        conn.executemany(
            """INSERT INTO hallazgos (auditoria_id, proceso_afectado, hallazgo, observaciones, estado)
               VALUES (?, ?, ?, ?, 'Pendiente')""",
            [(auditoria_id, h[0], h[1], h[2]) for h in hallazgos]
        )


# ── Botiquín ───────────────────────────────────────────────────────────────────

def get_botiquin(auditoria_id: int) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql(
            "SELECT * FROM botiquin WHERE auditoria_id = ?",
            conn, params=(auditoria_id,)
        )


def update_botiquin_item(item_id: int, item: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE botiquin SET item = ? WHERE id = ?", (item, item_id))


def update_botiquin_unidades(item_id: int, unidades: str | None) -> None:
    with get_db() as conn:
        conn.execute("UPDATE botiquin SET unidades = ? WHERE id = ?", (unidades, item_id))


def update_botiquin_fecha(item_id: int, fecha: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE botiquin SET fecha_vencimiento = ? WHERE id = ?", (fecha, item_id))


# ── Secciones Farma ────────────────────────────────────────────────────────────

def get_secciones_farma() -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql("SELECT * FROM secciones_farma", conn)


# ── Consolidado multi-tienda ───────────────────────────────────────────────────

def get_consolidado(tienda_id: str | None = None) -> pd.DataFrame:
    """
    Retorna todas las auditorías con métricas calculadas.
    Si tienda_id se especifica, filtra por esa tienda.
    """
    sql = """
        SELECT
            a.id,
            a.tienda_id,
            t.nombre   AS tienda_nombre,
            a.fecha,
            a.auditor,
            a.calificacion_global,
            a.resultado,
            (SELECT COUNT(*) FROM items_farma f WHERE f.auditoria_id = a.id)              AS total_farma,
            (SELECT COALESCE(SUM(f.puntaje),0) FROM items_farma f WHERE f.auditoria_id = a.id) AS cumple_farma,
            (SELECT COALESCE(AVG(it.calificacion),0) FROM items_tienda it WHERE it.auditoria_id = a.id) AS avg_tienda,
            (SELECT COUNT(*) FROM hallazgos h WHERE h.auditoria_id = a.id AND h.estado='Pendiente') AS hall_pend
        FROM auditorias a
        JOIN tiendas t ON t.id = a.tienda_id
    """
    params = ()
    if tienda_id:
        sql += " WHERE a.tienda_id = ?"
        params = (tienda_id,)
    sql += " ORDER BY a.fecha DESC"

    with get_db() as conn:
        return pd.read_sql(sql, conn, params=params if params else None)
