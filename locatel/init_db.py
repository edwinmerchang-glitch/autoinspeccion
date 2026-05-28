import sqlite3
import os

DB_PATH = "autoinspection.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS tiendas (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS auditorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tienda_id TEXT NOT NULL,
        fecha TEXT NOT NULL,
        auditor TEXT NOT NULL,
        calificacion_global REAL,
        resultado TEXT,
        FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
    );

    CREATE TABLE IF NOT EXISTS secciones_farma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS items_farma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditoria_id INTEGER NOT NULL,
        seccion_id INTEGER NOT NULL,
        item TEXT NOT NULL,
        puntaje INTEGER NOT NULL,
        observacion TEXT,
        FOREIGN KEY (auditoria_id) REFERENCES auditorias(id),
        FOREIGN KEY (seccion_id) REFERENCES secciones_farma(id)
    );

    CREATE TABLE IF NOT EXISTS items_tienda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditoria_id INTEGER NOT NULL,
        criterio TEXT NOT NULL,
        minimo REAL,
        superior REAL,
        meta REAL,
        calificacion REAL,
        FOREIGN KEY (auditoria_id) REFERENCES auditorias(id)
    );

    CREATE TABLE IF NOT EXISTS hallazgos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditoria_id INTEGER NOT NULL,
        proceso_afectado TEXT NOT NULL,
        hallazgo TEXT NOT NULL,
        observaciones TEXT,
        estado TEXT DEFAULT 'Pendiente',
        FOREIGN KEY (auditoria_id) REFERENCES auditorias(id)
    );

    CREATE TABLE IF NOT EXISTS botiquin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditoria_id INTEGER NOT NULL,
        item TEXT NOT NULL,
        unidades TEXT,
        fecha_vencimiento TEXT,
        FOREIGN KEY (auditoria_id) REFERENCES auditorias(id)
    );
    """)

    # Tiendas seed
    tiendas = [
        ("E101","LOCATEL GALERIAS"),("E102","LOCATEL CEDRITOS"),("E103","LOCATEL RESTREPO"),
        ("E104","LOCATEL CALLE 116"),("E105","LOCATEL MALL PLAZA EL CASTILLO"),
        ("E106","LOCATEL HACIENDA SANTA BARBARA"),("E107","LOCATEL CALLE 100"),
        ("E108","LOCATEL SALITRE"),("E110","LOCATEL CALIMA"),("E111","LOCATEL PLAZA DE LAS AMERICAS"),
        ("E112","LOCATEL HAYUELOS"),("E113","LOCATEL CHAPINERO"),("E116","PASEO VILLA DEL RIO"),
        ("E117","CHIA"),("E201","LOCATEL OVIEDO"),("E202","LOCATEL CITY PLAZA"),
        ("E203","LOCATEL LA CEJA"),("E204","LOCATEL VIVA ENVIGADO"),
        ("E205","LOCATEL VIVA LAURELES"),("E206","LOCATEL SAN ANTONIO"),
        ("E600","BODEGA"),("E610","CEDI MEDELLIN"),
    ]
    c.executemany("INSERT OR IGNORE INTO tiendas VALUES (?,?)", tiendas)

    # Secciones farma
    secciones = [
        (1, "DOCUMENTACIÓN LEGAL Y TÉCNICA"),
        (2, "INFRAESTRUCTURA Y ÁREAS"),
        (3, "REGISTROS Y PROCESOS"),
        (4, "ÁREA DE INYECTOLOGÍA"),
    ]
    c.executemany("INSERT OR IGNORE INTO secciones_farma VALUES (?,?)", secciones)

    conn.commit()

    # Seed auditoria E103 si no existe
    existing = c.execute("SELECT id FROM auditorias WHERE tienda_id='E103' AND fecha='2025-08-10'").fetchone()
    if not existing:
        c.execute("""INSERT INTO auditorias (tienda_id, fecha, auditor, calificacion_global, resultado)
                     VALUES ('E103', '2025-08-10', 'EDWIN MERCHÁN', 0.82, 'DESFAVORABLE')""")
        audit_id = c.lastrowid

        # Items farma - Sección 1: Documentación legal
        items_sec1 = [
            ("Acta delegación atención de visitas de los entes Reguladores y manejo de medicamentos de control especial (MCE)", 1, "ok"),
            ("Certificado de uso de suelos", 1, "exp 13 nov 2020"),
            ("Registro mercantil (camara comercio)", 1, "actualizada 10-03-2025"),
            ("Certificado de bomberos", 0, "se genera recibo de pago"),
            ("Extintores vigentes", 1, "vigentes hasta 07/2026"),
            ("Certificado de Sayco y Acinpro", 1, "vigente hasta 31/12/2025"),
            ("Certificado de representacion legal", 1, "OK"),
            ("Rut", 1, "10/03/2025 actual"),
            ("Camara de comercio -actualizada año", 1, "actualizada 19-05-2025"),
            ("Certificado de calibracion de termometro y termohigrometros (Vigencia 1año)", 1, "vigente 04/03/2026"),
            ("Certificación Mantenimiento de neveras", 1, "Realizada 29/10/2024"),
            ("Acta de la visita de la secretaria de la bodega.", 1, "favorable 18/09/2024"),
            ("Acta de visita secretaria de salud proveedores", 1, "AXA 13 mazo 2025"),
            ("Actas de visita de Secretaria de Salud tienda", 1, "Requerimientos 13/05/2025"),
            ("Informes enviados al FNE y SUB RED correspondiente", 1, "ok"),
            ("Recepcion de MCE-Lote-registro invima,fecha vencimiento", 1, "ok"),
            ("Devoluciones de MCE-Soporte correo cendis", 1, "ok"),
            ("Resolucion de medicamentos de control(vigencia 5 años)", 1, "Vigente 27/07/2023"),
            ("Formulas con sello despachado,datos de paciente(nombre,cedula,direccion,telefono)", 1, "ok"),
            ("libro con formulas descargadas al dia", 1, "ok"),
            ("Carta de autorizacion de venta de controlados auxiliares", 1, "ok"),
            ("Capacitacion del procedimiento de medicamentos de control.", 1, "ok"),
            ("Conciliacion libro-fisico-sitema de medicamentos de control", 1, "ok"),
            ("Organización por orden alfabetico MCE", 1, "ok"),
            ("Diploma de director tecnico.", 1, "ok"),
            ("Resolucion de regente de farmacia", 1, "ok"),
            ("contrato del director tecnico", 1, "ok"),
            ("Tarjeta de auxiliares de farmacia", 1, "rethus"),
            ("hoja de vida del personal", 1, "ok"),
            ("Soporte de capacitacion en manejo higienico de alimentos. (Vigencia 1 año)", 1, "Realizado 27/02/2025"),
            ("Examen medico personal tienda (Vigencia 1 año)", 1, "Gestion humana"),
            ("ARL personal tienda", 1, "ok"),
            ("Contrato de empresa manejo de residuos-manifiesto.", 1, "activo mayo 2025"),
            ("Radicado anual de residuos -soportes", 1, "Radicado 03/01/2025"),
            ("Radicado mensual de residuos -soportes", 1, "ULTIMO 06/08/2025"),
            ("Certificado Lavado de Tanques 6 meses", 1, "Realizado 04/04/2025"),
            ("Certificado de fumigacion 6 meses", 1, "Reaizada 01/04/2025"),
            ("Plano de ruta sanitaria", 1, "ok"),
            ("Cuadro de quejas", 1, "ok"),
            ("Informe de satisfacion al usuario", 1, "ok"),
            ("Farmacovigilancia", 1, "ok"),
            ("Tecnovigilancia", 1, "ok"),
            ("Plan de saneamiento", 1, "ok"),
            ("Certificados de inyectologia.(Auxiliares de farmacia)", 1, "ok"),
            ("Aviso de area libre de humo (ley 1335 de 2009)", 1, "ok"),
            ("Está prohibida la venta de alcohol industrial y antiséptico a niños, niñas y adolescentes.", 1, "ok"),
            ("Prohibido el ingreso de mascotas. Resolución 2674 de 2013", 1, "ok"),
            ("Notificación director técnico FNE", 1, "ok"),
            ("Formatos de Áreas de responsabilidad", 0, "Muy pocas auditorias de inspección de limpieza"),
        ]
        c.executemany("INSERT INTO items_farma (auditoria_id, seccion_id, item, puntaje, observacion) VALUES (?,1,?,?,?)",
                      [(audit_id, i[0], i[1], i[2]) for i in items_sec1])

        # Sección 2: Infraestructura
        items_sec2 = [
            ("Pisos material,impermeable facil limpieza y sanitizacion", 1, "ok"),
            ("Paredes son impermeables de facil limpieza y sanitizacion limpias y sin humedad.", 1, "ok"),
            ("Techos y cielos rasos deben ser resistentes ,uniformes y de facil limpieza y sanitizacion", 1, "ultima 30 agosto 2024"),
            ("Independiencia de la drogueria", 1, "ok"),
            ("Redes electricas en buen estado(tomas,interruptores y cableado protegido)", 1, "ok"),
            ("Area de medicamentos de control (avisos)", 1, "ok"),
            ("Area administrativa (avisos)", 1, "ok"),
            ("Area de recepcion Tecnica (avisos)", 1, "ok"),
            ("Area de almacenamiento (avisos)", 1, "ok"),
            ("Area de dispensacion (avisos)", 1, "ok"),
            ("Area restringida (Prohibido el ingresa a personal no autorizado)", 1, "ok"),
            ("Area de medicamentos refrigerados (avisos)", 1, "ok"),
            ("Area de cuarentena (avisos)", 1, "ok"),
            ("Area de medicamentos proximos a vencer (avisos)", 1, "ok"),
            ("Area de averias (avisos)", 1, "ok"),
            ("Area de residuos (avisos)", 1, "ok"),
            ("Area Inyectología (avisos)", 1, "ok"),
            ("organización medicamentos lassa", 0, "falta categorizar varios medicamentos"),
            ("CONTROL PEPS", 0, "no se cumple en su totalidad"),
            ("Almacenamiento (Droga blanca)", 1, "ok"),
            ("Almacenamiento Fitoterapeuticos", 1, "ok"),
            ("Almacenamiento Homeopaticos", 1, "ok"),
            ("Almacenamiento dispositivos medicos", 1, "ok"),
            ("Caneca negra: cocina, baño", 1, "ok"),
            ("Caneca blanca: oficina, drogueria.", 1, "ok"),
            ("Suficientes estibas para procedimiento de almacenamiento", 1, "ok"),
            ("Almacenamiento (Suplementos dietarios)", 1, "ok"),
        ]
        c.executemany("INSERT INTO items_farma (auditoria_id, seccion_id, item, puntaje, observacion) VALUES (?,2,?,?,?)",
                      [(audit_id, i[0], i[1], i[2]) for i in items_sec2])

        # Sección 3: Registros
        items_sec3 = [
            ("Información al usuario(Volantes) registros de entrega totalmente diligenciados.", 1, "ok"),
            ("Recepcion de medicamentos", 1, "ok"),
            ("Recepcion de medicamentos refrigerados(CDF hora-temperatura-Tienda hora-temperatura)", 1, "ok"),
            ("Registros condiciones ambientales.", 1, "ok"),
            ("temperatura de nevera-refrigerados", 1, "ok"),
            ("temperatura de nevera-congelados", 1, "ok"),
            ("temperaturas de nevera de medicamentos", 1, "ok"),
            ("temperatura y humedad de farmacia", 1, "ok"),
            ("temperatura y humedad de otc", 1, "ok"),
            ("temperatura y humedad de inyectogia", 1, "ok"),
            ("temperatura y humedad de bodega", 1, "ok"),
            ("Registro limpieza y desinfeccion area de droguería", 1, "ok"),
            ("Registro de limpieza areas internas:pasillos , escaleras y cafeteria.", 1, "ok"),
            ("Registro de limpieza de cuarto de aseo,limpieza y desinfeccion baño.", 1, "ok"),
            ("Registros devoluciones de medicamentos a la bodega.", 1, "ok"),
            ("Registros entrega medicamentos refrigerados al usuario-libro", 1, "ok"),
            ("Registros de informacion al usuario y estilos de vida saludable.", 1, "ok"),
            ("Socializacion según cronograma.", 1, "ok"),
            ("Capacitacion de procedimientos misionales(todo el personal ,acta ,asistencia,evaluacion)", 1, "ok"),
            ("Cuadro de quejas", 1, "ok"),
            ("Informe de satisfacion al usuario", 1, "ok"),
            ("Matriz de riesgos", 1, "ok"),
            ("Indicadores de gestion", 1, "ok"),
            ("Correo a compras -no codificados", 1, "ok"),
            ("Correo a compras -agotados", 1, "ok"),
            ("Auditorias", 1, "ultima 24/02/2025"),
            ("Plan de mejoramiento continuo", 0, "no se realizó en el tiempo determinado"),
            ("Fotos de soporte formulas area de domicilios", 0, "no se estan recolectando"),
        ]
        c.executemany("INSERT INTO items_farma (auditoria_id, seccion_id, item, puntaje, observacion) VALUES (?,3,?,?,?)",
                      [(audit_id, i[0], i[1], i[2]) for i in items_sec3])

        # Sección 4: Inyectología
        items_sec4 = [
            ("Botiquin (Area de inyectologia)", 1, "ok"),
            ("caneca roja,negra,blanca :inyectologia", 1, "ok"),
            ("Guardianes", 1, "ok"),
            ("Camillas en orden y limpios", 1, "ok"),
            ("Sábana en buen estado", 1, "ok"),
            ("libro de inyectologia diligenciado EN SU TOTALIDAD ,firma del consentimiento del cliente.", 1, "ok"),
            ("Registro limpieza y desinfección área inyectología", 1, "ok"),
            ("Formato para el resultado de la glucometria", 1, "no aplica"),
            ("Registro en planilla toma de glucometría.", 1, "no aplica"),
            ("glucometro en funcionamiento", 1, "no aplica"),
            ("tiras de glucometria(fecha de vencimiemto)", 1, "no aplica"),
            ("guardian,guantes,alcohol,toallas desechables, jabón,jeringas", 1, "ok"),
            ("escalera", 1, "ok"),
        ]
        c.executemany("INSERT INTO items_farma (auditoria_id, seccion_id, item, puntaje, observacion) VALUES (?,4,?,?,?)",
                      [(audit_id, i[0], i[1], i[2]) for i in items_sec4])

        # Items tienda
        items_tienda = [
            ("PRESENTACION PERSONAL ADMINISTRATIVO", 9, 9.5, 10, 9.5),
            ("PRESENTACION PERSONAL FUNCIONARIOS", 9, 9.5, 10, 9.5),
            ("IDENTIFICACION FUNCIONARIOS", 9, 9.5, 10, 9.0),
            ("ASEO Y ORDEN TIENDA", 9, 9.5, 10, 8.5),
            ("ASEO Y ORDEN BODEGA", 9, 9.5, 10, 8.5),
            ("ASEO Y ORDEN DOMICILIOS", 9, 9.5, 10, 8.5),
            ("ASEO ORDEN DROGUERIA", 9, 9.5, 10, 9.5),
            ("MANTENIMIENTO F.V", 9, 9.5, 10, 9.5),
            ("CONTROL AVERIAS Y MERMA", 9, 9.5, 10, 9.5),
            ("AUTOINSPECCION", 9, 9.5, 10, 0.0),
        ]
        c.executemany("INSERT INTO items_tienda (auditoria_id, criterio, minimo, superior, meta, calificacion) VALUES (?,?,?,?,?,?)",
                      [(audit_id,) + i for i in items_tienda])

        # Hallazgos
        hallazgos = [
            ("Bomberos", "Pendiente visita ya se generó recibo de pago", None, "Pendiente"),
            ("Áreas de responsabilidad", "No se realizó auditoria a todas las áreas de responsabilidad", None, "Pendiente"),
            ("Organización LASA", "Falta por señalizar y categorizar varios medicamentos a los que les aplica esta marcación", None, "Pendiente"),
            ("Control PEPS", "Se evidencia productos con fecha corta al fondo de la gondola", None, "Pendiente"),
            ("Plan de mejora continua", "No se realizó el plan de mejora en el tiempo determinado para el proceso", None, "Pendiente"),
            ("Fotos fórmulas medicamentos domicilios", "No se esta tomando evidencia fotográfica de formulas dispensadas en el área de domicilios", None, "Pendiente"),
        ]
        c.executemany("INSERT INTO hallazgos (auditoria_id, proceso_afectado, hallazgo, observaciones, estado) VALUES (?,?,?,?,?)",
                      [(audit_id,) + h for h in hallazgos])

        # Botiquín
        botiquin = [
            ("GASAS LIMPIAS PAQUETE", "PAQUETE X 20", "2029-04-01"),
            ("ESPARADRAPO TELA ROLLO 4 PULGADAS", "UNIDAD", "2025-09-01"),
            ("BAJALENGUAS X 20 UNID", "PAQUETE X 20", "2028-03-01"),
            ("GUANTES LATEX EXAMEN", "CAJA X10", "2028-05-01"),
            ("VENDA ELASTICA 2 X 5 YARDAS", "UNIDAD", "2026-05-01"),
            ("VENDA ELASTICA 3 X 5 YARDAS", "UNIDAD", "2029-12-01"),
            ("VENDA ELASTICA 5 X 5 YARDAS", "UNIDAD", "2028-10-01"),
            ("VENDA ALGODON 3 X 5 YARDAS", "UNIDAD", "2026-06-01"),
            ("VENDA ALGODON 4 X 5 YARDAS", "UNIDAD", "2026-09-01"),
            ("YODOPOVIDONA *JABON QUIRURGICO", "UNIDAD", "2026-05-01"),
            ("SOLUCION SALINA 500 ML", "UNIDAD", "2025-10-01"),
            ("TERMOMETRO DIGITAL UNIDAD", "UNIDAD", None),
            ("ALCOHOL ANTISEPTICO 350 ML", "UNIDAD", "2025-12-01"),
            ("ALGODÓN 25GRS", "UNIDAD", "2026-08-01"),
        ]
        c.executemany("INSERT INTO botiquin (auditoria_id, item, unidades, fecha_vencimiento) VALUES (?,?,?,?)",
                      [(audit_id,) + b for b in botiquin])

        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada correctamente.")
