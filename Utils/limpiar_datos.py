import sqlite3

def limpiar_resultados():
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()

    try:
        # Borramos los eventos descargados
        cursor.execute("DELETE FROM eventos")
        # Borramos los bloques creados
        cursor.execute("DELETE FROM bloques")
        
        # Opcional: Reiniciar los contadores de ID a 0
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='eventos'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='bloques'")
        
        conexion.commit()
        print("Tablas de resultados limpias. Tu biblioteca de eventos está intacta.")
    except Exception as e:
        print(f"Error al limpiar: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    limpiar_resultados()