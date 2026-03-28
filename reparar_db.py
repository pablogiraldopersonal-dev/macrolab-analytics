import sqlite3

def reparar_final():
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()
    
    # Lista de tablas que necesitan la columna user_id
    tablas = ["bloques", "eventos", "eventos_raw"]

    for tabla in tablas:
        try:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN user_id INTEGER")
            print(f"✓ Columna user_id añadida a {tabla}")
        except sqlite3.OperationalError:
            print(f"- La columna ya existe en {tabla}")

    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    reparar_final()