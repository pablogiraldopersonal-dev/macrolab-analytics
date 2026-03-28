import sqlite3

def crear_equipo():
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()

    # PASO 1: CREAR LA TABLA SI NO EXISTE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT,
            estado TEXT DEFAULT 'Desconectado'
        )
    """)

    # PASO 2: LISTA DEL EQUIPO
    equipo = [
        ('pablo_giraldo', 'CEO_Macro_2026', 'PABLO GIRALDO'),
        ('juan_trader', 'J7821_MLA', 'JUAN'),
        ('jairo_macro', 'J9902_MLA', 'JAIRO'),
        ('daniela_data', 'D4412_MLA', 'DANIELA'),
        ('ivon_quitian', 'I7763_MLA', 'IVON QUITIAN'),
        ('angelo_alfonso', 'A5514_MLA', 'ANGELO ALFONSO'),
        ('juan_giraldo', 'JG_9921_MLA', 'JUAN GIRALDO')
    ]

    # PASO 3: INSERTAR O ACTUALIZAR
    for user, pw, nombre in equipo:
        cursor.execute("""
            INSERT OR REPLACE INTO usuarios (username, password, nombre_completo, estado) 
            VALUES (?, ?, ?, 'Desconectado')
        """, (user, pw, nombre))

    conexion.commit()
    conexion.close()
    print("¡LISTO! Tabla creada y equipo cargado sin errores.")

if __name__ == "__main__":
    crear_equipo()