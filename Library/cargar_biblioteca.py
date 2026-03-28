import sqlite3
import json

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

cursor.execute("DELETE FROM biblioteca_eventos")

eventos = [

# ================================
# NUCLEO FUERTE USD
# ================================

(
"NFP - Bloque Laboral USD",
"NUCLEO",
"USD",
"Mayor lectura → USD ↑ | Menor lectura → USD ↓",
"Primer viernes de cada mes",
"Puede modificarse por razones oficiales",
"Bloque estructural completo del mercado laboral estadounidense.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "Nonfarm Payrolls", "descripcion": "Variación mensual del empleo excluyendo agricultura."},
        {"nombre": "Unemployment Rate", "descripcion": "Tasa de desempleo."},
        {"nombre": "Average Hourly Earnings", "descripcion": "Variación mensual de salarios."}
    ],
    "secundario": [
        {"nombre": "Average Hourly Earnings", "descripcion": "Crecimiento anual salarial."},
        {"nombre": "Participation Rate", "descripcion": "Participación laboral."},
        {"nombre": "Average Weekly Hours", "descripcion": "Horas trabajadas."},
        {"nombre": "Private Nonfarm Payrolls", "descripcion": "Empleo privado."},
        {"nombre": "Manufacturing Payrolls", "descripcion": "Empleo manufacturero."},
        {"nombre": "U-6 Underemployment Rate", "descripcion": "Subempleo ampliado."}
    ]
})
),

(
"CPI - Inflación USD",
"NUCLEO",
"USD",
"Mayor lectura → USD ↑ | Menor lectura → USD ↓",
"Mensual",
"Si Core y Headline divergen el bloque se vuelve mixto",
"Inflación al consumidor.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "CPI", "descripcion": "Inflación general."},
        {"nombre": "Core CPI", "descripcion": "Inflación subyacente."}
    ],
    "secundario": [
        {"nombre": "CPI", "descripcion": "Variación anual."},
        {"nombre": "Core CPI", "descripcion": "Core anual."}
    ]
})
),

(
"PCE - Inflación Preferida Fed",
"NUCLEO",
"USD",
"Mayor lectura → USD ↑ | Menor lectura → USD ↓",
"Mensual (final de mes)",
"La Fed observa principalmente el Core PCE",
"Bloque de inflación preferido por la Reserva Federal.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "Core PCE Price Index", "descripcion": "Inflación subyacente mensual."},
        {"nombre": "Core PCE Price Index", "descripcion": "Inflación subyacente anual."}
    ],
    "secundario": [
        {"nombre": "PCE Price Index", "descripcion": "Inflación general."},
        {"nombre": "Personal Income", "descripcion": "Ingreso personal."},
        {"nombre": "Personal Spending", "descripcion": "Gasto personal."}
    ]
})
),

(
"Interest Rate Decision - Fed",
"NUCLEO",
"USD",
"Subida de tasa → USD ↑ | Recorte → USD ↓",
"Ocho veces al año",
"Solo operable por dato numérico de tasa",
"Decisión oficial de la tasa de interés de la Reserva Federal.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "Fed Interest Rate Decision", "descripcion": "Tasa oficial."}
    ],
    "secundario": []
})
),

# ================================
# CONDICIONALES USD
# ================================

(
"ISM Manufacturing PMI",
"CONDICIONAL",
"USD",
"Mayor lectura → USD ↑ | Menor lectura → USD ↓",
"Mensual",
"",
"Indicador manufacturero adelantado.",
json.dumps({
    "relevancia_bloque": "CONDICIONAL",
    "nucleo": [
        {"nombre": "ISM Manufacturing PMI", "descripcion": "Actividad manufacturera."}
    ],
    "secundario": [
        {"nombre": "ISM Manufacturing Employment", "descripcion": "Subcomponente laboral."},
        {"nombre": "ISM Manufacturing Prices", "descripcion": "Subcomponente precios."}
    ]
})
),

(
"ISM Non-Manufacturing PMI",
"CONDICIONAL",
"USD",
"Mayor lectura → USD ↑ | Menor lectura → USD ↓",
"Mensual",
"Representa el sector servicios (+70% del PIB de EE.UU.)",
"Indicador adelantado del sector servicios.",
json.dumps({
    "relevancia_bloque": "CONDICIONAL",
    "nucleo": [
        {"nombre": "ISM Non-Manufacturing PMI", "descripcion": "Actividad del sector servicios."}
    ],
    "secundario": [
        {"nombre": "ISM Non-Manufacturing Employment", "descripcion": "Subcomponente laboral servicios."},
        {"nombre": "ISM Non-Manufacturing Prices", "descripcion": "Subcomponente precios servicios."}
    ]
})
),

(
"Philly Fed Manufacturing Index",
"CONDICIONAL",
"USD",
"Mayor lectura → USD ↑ | Menor lectura → USD ↓",
"Mensual",
"",
"Indicador regional manufacturero.",
json.dumps({
    "relevancia_bloque": "CONDICIONAL",
    "nucleo": [
        {"nombre": "Philly Fed Manufacturing Index", "descripcion": "Actividad regional."}
    ],
    "secundario": []
})
),

# ================================
# NUCLEO FUERTE CAD
# ================================

(
"Employment Change - Bloque Laboral CAD",
"NUCLEO",
"CAD",
"Mayor lectura → CAD ↑ | Menor lectura → CAD ↓",
"Mensual",
"",
"Bloque laboral canadiense.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "Employment Change", "descripcion": "Cambio empleo."},
        {"nombre": "Unemployment Rate", "descripcion": "Desempleo."}
    ],
    "secundario": [
        {"nombre": "Full Employment Change", "descripcion": "Empleo tiempo completo."},
        {"nombre": "Part Time Employment Change", "descripcion": "Empleo parcial."}
    ]
})
),

(
"CPI - Inflación CAD",
"NUCLEO",
"CAD",
"Mayor lectura → CAD ↑ | Menor lectura → CAD ↓",
"Mensual",
"",
"Inflación canadiense.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "CPI", "descripcion": "Inflación general."},
        {"nombre": "Core CPI", "descripcion": "Inflación subyacente."}
    ],
    "secundario": []
})
),

(
"Interest Rate Decision - BoC",
"NUCLEO",
"CAD",
"Subida de tasa → CAD ↑ | Recorte → CAD ↓",
"Ocho veces al año",
"",
"Decisión del Banco de Canadá.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "BoC Interest Rate Decision", "descripcion": "Tasa oficial."}
    ],
    "secundario": []
})
),

(
"GDP - Canadá",
"CONDICIONAL",
"CAD",
"Mayor lectura → CAD ↑ | Menor lectura → CAD ↓",
"Mensual",
"",
"PIB mensual canadiense.",
json.dumps({
    "relevancia_bloque": "CONDICIONAL",
    "nucleo": [
        {"nombre": "GDP", "descripcion": "Crecimiento mensual."}
    ],
    "secundario": []
})
),

# ================================
# EUR
# ================================

(
"CPI - Inflación EUR",
"NUCLEO",
"EUR",
"Mayor lectura → EUR ↑ | Menor lectura → EUR ↓",
"Mensual",
"",
"Inflación zona euro.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "CPI", "descripcion": "Inflación general."},
        {"nombre": "Core CPI", "descripcion": "Inflación subyacente."}
    ],
    "secundario": []
})
),

(
"Interest Rate Decision - ECB",
"NUCLEO",
"EUR",
"Subida → EUR ↑ | Recorte → EUR ↓",
"Ocho veces al año",
"",
"Decisión ECB.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "ECB Interest Rate Decision", "descripcion": "Tasa oficial."}
    ],
    "secundario": []
})
),

# ================================
# GBP
# ================================

(
"CPI - Inflación GBP",
"NUCLEO",
"GBP",
"Mayor lectura → GBP ↑ | Menor lectura → GBP ↓",
"Mensual",
"",
"Inflación Reino Unido.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "CPI", "descripcion": "Inflación general."},
        {"nombre": "Core CPI", "descripcion": "Inflación subyacente."}
    ],
    "secundario": [
        {"nombre": "CPI", "descripcion": "Variación mensual."}
    ]
})
),

# ================================
# AUD
# ================================

(
"CPI_AUD",
"NUCLEO",
"AUD",
"Mayor lectura → AUD ↑ | Menor lectura → AUD ↓",
"Trimestral",
"",
"Inflación australiana.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "CPI", "descripcion": "Dato de inflación"}
    ],
    "secundario": []
})
),
(
"GDP_AUD",
"NUCLEO",
"AUD",
"Mayor lectura → AUD ↑ | Menor lectura → AUD ↓",
"Trimestral",
"",
"Crecimiento económico Australia.",
json.dumps({
    "relevancia_bloque": "NUCLEO",
    "nucleo": [
        {"nombre": "GDP", "descripcion": "Crecimiento trimestral/anual"}
    ],
    "secundario": []
})
),

]

cursor.executemany("""
INSERT INTO biblioteca_eventos
(nombre, categoria, divisa, regla_rapida, periodicidad, nota_excepcion, descripcion, acompanantes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", eventos)

conexion.commit()
conexion.close()

print("✅ BIBLIOTECA SINCRONIZADA: Relevancias inyectadas en acompañantes JSON.")