import sqlite3
import json

conn = sqlite3.connect("macrolab.db")
cursor = conn.cursor()

cursor.execute("SELECT nombre, divisa, acompanantes FROM biblioteca_eventos")

rows = cursor.fetchall()

for nombre, divisa, acompanantes in rows:
    print("BLOQUE:", nombre, divisa)

    data = json.loads(acompanantes)

    print("NUCLEO:")
    for n in data.get("nucleo", []):
        print("   ", n["nombre"])

    print("SECUNDARIO:")
    for s in data.get("secundario", []):
        print("   ", s["nombre"])

    print("--------------------")

conn.close()