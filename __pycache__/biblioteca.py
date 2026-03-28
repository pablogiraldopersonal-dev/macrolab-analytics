from flask import render_template
import sqlite3
import json

def registrar_biblioteca(app):

    @app.route("/biblioteca")
    def biblioteca():

        conexion = sqlite3.connect("macrolab.db")
        cursor = conexion.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            categoria TEXT,
            divisa TEXT,
            regla_rapida TEXT,
            periodicidad TEXT,
            nota_excepcion TEXT,
            descripcion TEXT,
            acompanantes TEXT
        )
        """)

        cursor.execute("SELECT * FROM biblioteca_eventos ORDER BY categoria")
        datos = cursor.fetchall()

        conexion.close()

        nucleos = []
        secundarios = []
        condicionales = []

        for e in datos:

            # Cargar JSON seguro
            if e[8]:
                try:
                    acompanantes = json.loads(e[8])
                except:
                    acompanantes = {}
            else:
                acompanantes = {}

            # Forzar estructura correcta
            if isinstance(acompanantes, list):
                acompanantes = {
                    "nucleo": acompanantes,
                    "secundario": []
                }

            if "nucleo" not in acompanantes:
                acompanantes["nucleo"] = []

            if "secundario" not in acompanantes:
                acompanantes["secundario"] = []

            evento = {
                "id": e[0],
                "nombre": e[1],
                "categoria": e[2],
                "divisa": e[3],
                "regla": e[4],
                "periodicidad": e[5],
                "nota": e[6],
                "descripcion": e[7],
                "acompanantes": acompanantes
            }

            if e[2] == "NUCLEO":
                nucleos.append(evento)
            elif e[2] == "SECUNDARIO":
                secundarios.append(evento)
            else:
                condicionales.append(evento)

        return render_template(
            "biblioteca.html",
            nucleos=nucleos,
            secundarios=secundarios,
            condicionales=condicionales
        )