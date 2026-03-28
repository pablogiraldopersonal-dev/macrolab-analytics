import sqlite3
from Core.bloques_macro import BLOQUES
from Core.bloques_macro import CATEGORIAS_MAPA

def inicializar_db():
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()

    # TABLA DE USUARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nombre_completo TEXT,
        rol TEXT DEFAULT 'trader',
        estado TEXT DEFAULT 'Desconectado',
        foto_perfil TEXT DEFAULT 'default_user.png',
        ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # TABLA DE BLOQUES (AÑADIDO user_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bloques (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fecha TEXT,
        hora TEXT,
        divisa TEXT,
        tipo_bloque TEXT,
        categoria TEXT,
        sesgo_previo TEXT DEFAULT 'Neutral',
        sesgo_real TEXT,
        clasificacion TEXT,
        sugerencia TEXT,
        descripcion TEXT,
        FOREIGN KEY(user_id) REFERENCES usuarios(id)
    )
    """)

    # TABLA DE EVENTOS (AÑADIDO user_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        bloque_id INTEGER,
        nombre_evento TEXT,
        prevision TEXT,
        anterior TEXT,
        real TEXT,
        tipo_interno TEXT,
        orden_evento INTEGER,
        FOREIGN KEY(bloque_id) REFERENCES bloques(id),
        FOREIGN KEY(user_id) REFERENCES usuarios(id)
    )
    """)

    # TABLA DE EVENTOS RAW (AÑADIDO user_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fecha TEXT,
        hora TEXT,
        divisa TEXT,
        nombre TEXT,
        impacto INTEGER,
        forecast TEXT,
        previous TEXT,
        actual TEXT,
        FOREIGN KEY(user_id) REFERENCES usuarios(id)
    )
    """)

    conexion.commit()
    conexion.close()

def obtener_bloques(divisa=None, tipo=None, fecha_desde=None, fecha_hasta=None, user_id=None):
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()
    
    # FILTRO OBLIGATORIO: user_id
    query = "SELECT * FROM bloques WHERE user_id = ?"
    params = [user_id]

    if divisa and divisa != "Todos":
        query += " AND divisa = ?"
        params.append(divisa)

    if tipo and tipo != "Todos":
        query += " AND categoria = ?"
        params.append(tipo)

    if fecha_desde:
        query += " AND fecha >= ?"
        params.append(fecha_desde)

    if fecha_hasta:
        query += " AND fecha <= ?"
        params.append(fecha_hasta)

    query += " ORDER BY fecha DESC, hora DESC"
    cursor.execute(query, params)
    datos = cursor.fetchall()
    conexion.close()
    return datos

def obtener_bloque(id, user_id=None):
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()

    # Seguridad: Validamos que el bloque pertenezca al usuario
    cursor.execute("SELECT * FROM bloques WHERE id = ? AND user_id = ?", (id, user_id))
    bloque = cursor.fetchone()

    if not bloque:
        conexion.close()
        return None, []

    cursor.execute("""
    SELECT * FROM eventos
    WHERE bloque_id = ? AND user_id = ?
    ORDER BY orden_evento
    """, (id, user_id))
    
    eventos = cursor.fetchall()
    conexion.close()
    return bloque, eventos

def buscar_o_crear_bloque(cursor, fecha, hora, divisa, tipo, user_id, relevancia="NUCLEO"):
    # Buscamos si ya existe el bloque para ese usuario específico
    cursor.execute("""
    SELECT id FROM bloques
    WHERE fecha=? AND divisa=? AND tipo_bloque=? AND user_id=?
    """, (fecha, divisa, tipo, user_id))

    bloque = cursor.fetchone()
    if bloque:
        return bloque[0]

    # Si no existe, lo creamos asignándole el user_id
    cursor.execute("""
    INSERT INTO bloques
    (fecha, hora, divisa, tipo_bloque, categoria, sesgo_previo, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fecha, hora, divisa, tipo, relevancia, "Neutral", user_id))

    return cursor.lastrowid