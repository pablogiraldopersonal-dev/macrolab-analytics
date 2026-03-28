import sqlite3
from Core.bloques_macro import BLOQUES
from database import buscar_o_crear_bloque 
from services.analisis_macro import actualizar_analisis

def procesar_eventos_raw(user_id=None):
    print("\n" + "="*50)
    print("🔍 INICIANDO MOTOR DE ESCANEO")
    print("="*50)

    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT fecha, hora, divisa, nombre, forecast, previous, actual 
        FROM eventos_raw 
        WHERE user_id = ?
    """, (user_id,))
    eventos = cursor.fetchall()

    print("EVENTOS RAW ENCONTRADOS:", len(eventos))

    for evento in eventos:
        fecha, hora, divisa, nombre = evento[0], evento[1], evento[2], evento[3]

        for nombre_bloque, datos in BLOQUES.items():
            partes = nombre_bloque.split("_")

            if partes[-1] in ["USD","EUR","CAD","GBP","AUD"]:
                if partes[-1] != divisa:
                    continue

            es_nucleo = False

            for evento_nucleo in datos["nucleo"]:
                if evento_nucleo.lower() in nombre.lower():
                    es_nucleo = True
                    break

            if es_nucleo:
                print("BLOQUE DETECTADO:", nombre_bloque)

                relevancia_bloque = datos.get("relevancia_bloque", "NUCLEO")
                orden_eventos = datos["nucleo"] + datos["secundario"]
                orden_evento = 999

                for i, ref in enumerate(orden_eventos):
                    if nombre.lower().startswith(ref.lower()):
                        orden_evento = i
                        break

                bloque_id = buscar_o_crear_bloque(
                    cursor, fecha, hora, divisa, nombre_bloque, user_id, relevancia_bloque
                )

                cursor.execute("""
                    SELECT id FROM eventos
                    WHERE bloque_id=? AND nombre_evento=? AND user_id=?
                """, (bloque_id, nombre, user_id))

                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO eventos
                        (bloque_id, user_id, nombre_evento, prevision, anterior, real, tipo_interno, orden_evento)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        bloque_id,
                        user_id,
                        nombre,
                        evento[4],
                        evento[5],
                        evento[6],
                        relevancia_bloque,
                        orden_evento
                    ))

                    for evento_sec in datos.get("secundario", []):
                        cursor.execute("""
                            SELECT fecha, hora, divisa, nombre, forecast, previous, actual
                            FROM eventos_raw
                            WHERE fecha=? AND hora=? AND divisa=? AND lower(nombre) LIKE ? AND user_id=?
                        """, (fecha, hora, divisa, f"%{evento_sec.lower()}%", user_id))

                        secundarios = cursor.fetchall()

                        for sec in secundarios:
                            nombre_sec = sec[3]

                            if nombre_sec.lower() == nombre.lower():
                                continue

                            cursor.execute("""
                                SELECT id FROM eventos
                                WHERE bloque_id=? AND nombre_evento=? AND user_id=?
                            """, (bloque_id, nombre_sec, user_id))

                            if not cursor.fetchone():
                                orden_evento_sec = 999

                                for i, ref in enumerate(orden_eventos):
                                    if nombre_sec.lower().startswith(ref.lower()):
                                        orden_evento_sec = i
                                        break

                                cursor.execute("""
                                    INSERT INTO eventos
                                    (bloque_id, user_id, nombre_evento, prevision, anterior, real, tipo_interno, orden_evento)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    bloque_id,
                                    user_id,
                                    nombre_sec,
                                    sec[4],
                                    sec[5],
                                    sec[6],
                                    "Secundario",
                                    orden_evento_sec
                                ))

    conexion.commit()

    cursor.execute("SELECT id FROM bloques WHERE user_id = ?", (user_id,))
    bloques_ids = cursor.fetchall()

    for b in bloques_ids:
        actualizar_analisis(b[0])

    conexion.close()
    print("PROCESAMIENTO FINALIZADO")