# =====================================================
# BANDERAS POR DIVISA
# =====================================================

def obtener_bandera(divisa):
    divisa = divisa.upper().strip()

    if divisa == "USD":
        return "🇺🇸"
    elif divisa == "EUR":
        return "🇪🇺"
    elif divisa == "GBP":
        return "🇬🇧"
    elif divisa == "CAD":
        return "🇨🇦"
    elif divisa == "AUD":
        return "🇦🇺"
    elif divisa == "JPY":
        return "🇯🇵"
    else:
        return ""

        # =====================================================
# DETECTAR TIPO BLOQUE
# =====================================================

def detectar_tipo_bloque(nombre):
    nombre = nombre.lower()

    print("DETECTOR RECIBE:", nombre)

    if "non-farm" in nombre or "payroll" in nombre:
        return "NFP"
    if "consumer price" in nombre or "cpi" in nombre:
        return "CPI"
    if "pce" in nombre:
        return "PCE"
    if "gross domestic" in nombre or "gdp" in nombre:
        return "GDP"
    return "OTRO"