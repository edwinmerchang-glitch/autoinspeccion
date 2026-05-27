# 🏥 Autoinspección Locatel — Streamlit App

App moderna de autoinspección para tiendas Locatel con base de datos SQLite.

## Estructura

```
autoinspection_app/
├── app.py            # App principal de Streamlit
├── init_db.py        # Inicialización y seed de la base de datos
├── requirements.txt  # Dependencias Python
└── README.md
```

## Funcionalidades

- 📊 **Dashboard** — KPIs, gauges y resumen ejecutivo por auditoría
- 💊 **Auditoría Farma** — 117 ítems organizados en 4 secciones con filtros
- 🏪 **Auditoría Tienda** — 10 criterios operativos con gráficos comparativos
- ⚠️ **Hallazgos** — Gestión de no conformidades con flujo de resolución
- 🩺 **Botiquín** — Control de vencimientos de elementos de primeros auxilios
- ➕ **Nueva Auditoría** — Formulario para registrar nuevas inspecciones

## Despliegue en Streamlit Cloud

1. Sube esta carpeta a un repositorio de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Selecciona `app.py` como archivo principal
5. Haz clic en **Deploy** — ¡listo!

> **Nota:** La base de datos SQLite se crea automáticamente al iniciar la app.
> El seed con los datos de la auditoría E103 (10-08-2025) se inserta solo si no existe.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```
