import sqlite3

conn = sqlite3.connect("macrolab.db")
cursor = conn.cursor()

cursor.execute("SELECT tipo_bloque, categoria FROM bloques")

rows = cursor.fetchall()

for r in rows:
    print(r)

conn.close()