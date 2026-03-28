import sqlite3

def conectar():
    return sqlite3.connect("macrolab.db")

def obtener_bloques_db(divisa=None, tipo=None, fecha_desde=None, fecha_hasta=None, user_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    # FILTRO OBLIGATORIO: user_id
    query = "SELECT * FROM bloques WHERE user_id = ?"
    params = [user_id]

    if divisa:
        query += " AND divisa = ?"
        params.append(divisa)
    if tipo:
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

def eliminar_bloque_db(bloque_id, user_id=None):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        # Seguridad: Solo elimina si el bloque pertenece al usuario
        cursor.execute("DELETE FROM eventos WHERE bloque_id=? AND user_id=?", (bloque_id, user_id))
        cursor.execute("DELETE FROM bloques WHERE id=? AND user_id=?", (bloque_id, user_id))
        conexion.commit()
    except Exception as e:
        print(f"Error al eliminar bloque {bloque_id}: {e}")
        conexion.rollback()
    finally:
        conexion.close()
    
def guardar_eventos_raw_db(eventos, user_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    # Limpiamos solo los eventos raw del usuario actual
    cursor.execute("DELETE FROM eventos_raw WHERE user_id = ?", (user_id,))
    for e in eventos:
        cursor.execute("""
            INSERT INTO eventos_raw
            (fecha, hora, divisa, nombre, impacto, forecast, previous, actual, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["fecha"], e["hora"], e["divisa"], e["nombre"],
            e["impacto"], e["forecast"], e["previous"], e["actual"], user_id
        ))
    conexion.commit()
    conexion.close()

def obtener_bloque_detalle_db(bloque_id, user_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    # Seguridad: Validamos dueño
    cursor.execute("SELECT * FROM bloques WHERE id=? AND user_id=?", (bloque_id, user_id))
    bloque = cursor.fetchone()
    cursor.execute("SELECT * FROM eventos WHERE bloque_id=? AND user_id=?", (bloque_id, user_id))
    eventos = cursor.fetchall()
    conexion.close()
    return bloque, eventos

def actualizar_bloque_completo_db(id_bloque, datos_bloque, lista_eventos, user_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    # Seguridad: Solo actualiza si es el dueño
    cursor.execute("""
        UPDATE bloques 
        SET fecha=?, hora=?, divisa=? 
        WHERE id=? AND user_id=?
    """, (datos_bloque['fecha'], datos_bloque['hora'], datos_bloque['divisa'], id_bloque, user_id))

    for e in lista_eventos:
        cursor.execute("""
            UPDATE eventos
            SET nombre_evento=?, prevision=?, anterior=?, real=?, tipo_interno=?
            WHERE id=? AND user_id=?
        """, (e['nombre'], e['prevision'], e['anterior'], e['real'], e['tipo'], e['id'], user_id))
    conexion.commit()
    conexion.close()

def insertar_bloque_completo_db(datos_bloque, lista_eventos, tipo_bloque_detectado, user_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    # Insertamos con user_id
    cursor.execute("""
        INSERT INTO bloques (fecha, hora, divisa, tipo_bloque, user_id)
        VALUES (?, ?, ?, ?, ?)
    """, (datos_bloque['fecha'], datos_bloque['hora'], datos_bloque['divisa'], tipo_bloque_detectado, user_id))
    
    bloque_id = cursor.lastrowid
    for e in lista_eventos:
        cursor.execute("""
            INSERT INTO eventos
            (bloque_id, nombre_evento, prevision, anterior, real, tipo_interno, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            bloque_id, e['nombre'], e['prevision'], e['anterior'],
            e['real'] if e['real'] != "" else None, e['tipo'], user_id
        ))
    conexion.commit()
    conexion.close()
    return bloque_id

def eliminar_multiples_bloques_db(lista_ids, user_id=None):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        # Generar los marcadores ? para la consulta IN
        placeholders = ','.join(['?'] * len(lista_ids))
        
        # Seguridad: Solo borrar lo que pertenezca al usuario
        cursor.execute(f"DELETE FROM eventos WHERE bloque_id IN ({placeholders}) AND user_id=?", lista_ids + [user_id])
        cursor.execute(f"DELETE FROM bloques WHERE id IN ({placeholders}) AND user_id=?", lista_ids + [user_id])
        
        conexion.commit()
    except Exception as e:
        print(f"Error en eliminación masiva: {e}")
        conexion.rollback()
    finally:
        conexion.close()