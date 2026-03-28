import sqlite3
from Core.tipos_evento import obtener_tipo_evento
from Core.bloques_macro import BLOQUES # <-- Cambiado
from Core.pesos_macro import obtener_peso, es_dominante # <-- Cambiado

# =====================================================
# CATEGORIA A / B
# =====================================================

def categoria_bloque(tipo, divisa):
    if tipo in ["NFP", "CPI", "PCE", "GDP"]:
        return "A"
    return "B"

# =====================================================
# UTILIDAD PARA COMPARAR VALORES TEXTO
# =====================================================

def limpiar_valor(valor):
    if not valor:
        return None
    valor = valor.replace("%", "").replace("K", "")
    try:
        return float(valor)
    except:
        return None

# =====================================================
# SESGO PREVIO
# =====================================================

def calcular_sesgo_previo(eventos, tipo_bloque=None):
    score = 0
    dominante_resultado = None
    tipo_base = None
    if tipo_bloque and tipo_bloque in BLOQUES:
        tipo_base = BLOQUES[tipo_bloque].get("tipo_base")

    for e in eventos:
        nombre = e[2]
        forecast = limpiar_valor(e[3])
        anterior = limpiar_valor(e[4])
        if forecast is None or anterior is None: continue

        tipo_evento = obtener_tipo_evento(nombre)
        tipo = tipo_base if tipo_base else tipo_evento

        if tipo == "crecimiento":
            resultado = 1 if forecast > anterior else -1 if forecast < anterior else 0
        elif tipo == "inverso":
            resultado = 1 if forecast < anterior else -1 if forecast > anterior else 0
        elif tipo in ["inflacion", "tasas"]:
            resultado = 1 if forecast > anterior else -1 if forecast < anterior else 0
        else:
            resultado = 0

        peso = obtener_peso(nombre, tipo_bloque)
        if es_dominante(nombre, tipo_bloque) and resultado != 0:
            dominante_resultado = resultado
        score += resultado * peso

    if dominante_resultado is not None:
        return "Alcista" if dominante_resultado > 0 else "Bajista"
    return "Alcista" if score > 0 else "Bajista" if score < 0 else "Neutral"

# =====================================================
# SESGO REAL
# =====================================================

def calcular_sesgo_real(eventos):

    total = 0

    for e in eventos:
        nombre = e[2]
        forecast = limpiar_valor(e[3])
        real = limpiar_valor(e[5])
        tipo_interno = e[6]

        if real is None or forecast is None:
            continue

        tipo_evento = obtener_tipo_evento(nombre)
        peso = 2 if tipo_interno == "NUCLEO" else 1

        if tipo_evento == "crecimiento":
            resultado = peso if real > forecast else -peso if real < forecast else 0

        elif tipo_evento == "inverso":
            resultado = peso if real < forecast else -peso if real > forecast else 0

        elif tipo_evento == "inflacion":
            resultado = peso if real > forecast else -peso if real < forecast else 0

        elif tipo_evento == "tasas":
            resultado = peso if real > forecast else -peso if real < forecast else 0

        else:
            resultado = 0

        total += resultado

    if total > 0:
        return "Alcista"
    elif total < 0:
        return "Bajista"
    else:
        return "Neutral"

def clasificacion_simple(eventos, tipo_bloque):
    peso_pos = 0
    peso_neg = 0
    dominante = None

    for e in eventos:
        nombre = e[2]
        forecast = limpiar_valor(e[3])
        anterior = limpiar_valor(e[4])
        tipo_interno = e[6]
        if tipo_interno != "NUCLEO" or forecast is None or anterior is None: continue

        tipo_evento = obtener_tipo_evento(nombre)
        if tipo_evento == "crecimiento":
            resultado = 1 if forecast > anterior else -1 if forecast < anterior else 0
        elif tipo_evento == "inverso":
            resultado = 1 if forecast < anterior else -1 if forecast > anterior else 0
        elif tipo_evento in ["inflacion", "tasas"]:
            resultado = 1 if forecast > anterior else -1 if forecast < anterior else 0
        else:
            resultado = 0

        peso = obtener_peso(nombre, tipo_bloque)
        if es_dominante(nombre, tipo_bloque) and resultado != 0:
            dominante = resultado
        if resultado > 0: peso_pos += peso
        elif resultado < 0: peso_neg += peso

    if (peso_pos + peso_neg) == 0: return "No operable"

    if dominante is not None:
        if dominante == 1:
            return "Fuerte" if peso_pos >= peso_neg else "Moderado"
        if dominante == -1:
            return "Fuerte" if peso_neg >= peso_pos else "Moderado"

    if (peso_pos >= 5 and peso_neg == 0) or (peso_neg >= 5 and peso_pos == 0):
        return "Fuerte"
    if abs(peso_pos - peso_neg) <= 2:
        return "Mixto"
    return "Moderado"

# =====================================================
# DECISION OPERATIVA 🔥
# =====================================================

def decision_operativa(sesgo_previo, clasificacion, tipo_bloque):

    confianza = None

    if tipo_bloque in BLOQUES:
        confianza = BLOQUES[tipo_bloque].get("confianza")

    if confianza is None:
        return "No operable"

    if clasificacion == "Fuerte":

        if confianza in ["alta", "media"]:
            return "Operable"

        if confianza == "baja":
            return "Condicional"

    if clasificacion == "Moderado":
        return "Condicional"

    if clasificacion == "Mixto":
        return "Condicional"

    return "No operable"

# =====================================================
# tipo de ejecucion 
# =====================================================

def tipo_ejecucion(decision):

    if decision == "Operable":
        return "Orden por hora"

    if decision == "Condicional":
        return "Orden por cotización"

    return "No ejecutar"

# =====================================================
# ACTUALIZAR ANALISIS
# =====================================================

def actualizar_analisis(bloque_id):
    conexion = sqlite3.connect("macrolab.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM bloques WHERE id = ?", (bloque_id,))
    bloque = cursor.fetchone()

    cursor.execute("SELECT * FROM eventos WHERE bloque_id = ?", (bloque_id,))
    eventos = cursor.fetchall()

    tipo = bloque[4] # Ej: 'PCE_USD'

    # --- FIX AQUÍ ---
    from Core.bloques_macro import CATEGORIAS_MAPA
    # Buscamos 'PCE_USD' en el mapa para obtener 'Inflación'
    categoria_real = CATEGORIAS_MAPA.get(tipo, "Otros") 
    # ----------------

    sesgo_previo = calcular_sesgo_previo(eventos, tipo)
    clasificacion = clasificacion_simple(eventos, tipo)
    sesgo_real = calcular_sesgo_real(eventos)
    decision = decision_operativa(sesgo_previo, clasificacion, tipo)
    
    cursor.execute("""             
        UPDATE bloques
        SET 
            categoria = ?, 
            sesgo_previo = ?, 
            sesgo_real = ?, 
            clasificacion = ?, 
            sugerencia = ?
        WHERE id = ?
    """, (
        categoria_real, # <--- Guardamos el nombre real (Inflación, Empleo, etc.)
        sesgo_previo or "",
        sesgo_real or "",
        clasificacion or "",
        decision or "",
        bloque_id
    ))
    conexion.commit()
    conexion.close()