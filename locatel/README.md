# 🏥 Autoinspección Locatel — Streamlit App

App moderna de autoinspección para tiendas Locatel con base de datos SQLite.

## Estructura del proyecto

```
locatel/
├── app.py                     # Entrada principal: config, sidebar y routing
├── init_db.py                 # Inicialización y seed de la base de datos
├── requirements.txt
│
├── styles/
│   └── main.css               # Todo el CSS en un solo lugar
│
├── db/
│   ├── connection.py          # get_db() context manager + get_connection() legado
│   └── queries.py             # Todas las queries SQL centralizadas
│
├── components/
│   ├── ui.py                  # Gauge SVG, KPI cards, badges, helpers de color
│   └── exports.py             # Generación de reportes Excel
│
└── pages/
    ├── dashboard.py           # 📊 KPIs, gauges y resumen ejecutivo
    ├── farma.py               # 💊 117 ítems con puntaje y observación
    ├── tienda.py              # 🏪 10 criterios operativos
    ├── hallazgos.py           # ⚠️ CRUD de no conformidades
    ├── botiquin.py            # 🩺 Control de vencimientos
    └── nueva_auditoria.py     # ➕ Formulario de nueva auditoría
```

## Cómo agregar una nueva página

1. Crea `pages/mi_pagina.py` con una función `render(sel_aud_id)`.
2. Importa el módulo en `app.py`: `import pages.mi_pagina as pg_mi`.
3. Agrega la entrada en `NAV_ITEMS`.
4. Agrega el `elif` en el bloque de routing al final de `app.py`.

## Cómo agregar una query SQL

Agrega una función en `db/queries.py` usando el context manager `get_db()`:

```python
def get_mi_tabla(auditoria_id: int) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql("SELECT * FROM mi_tabla WHERE auditoria_id=?", conn, params=(auditoria_id,))
```

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube la carpeta `locatel/` a un repositorio de GitHub.
2. Ve a [share.streamlit.io](https://share.streamlit.io).
3. Conecta tu repositorio y selecciona `app.py` como archivo principal.
4. Haz clic en **Deploy**.

> La base de datos SQLite se crea automáticamente al iniciar la app.
