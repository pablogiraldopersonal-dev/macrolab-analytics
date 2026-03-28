def obtener_peso(nombre, tipo_bloque=None):
    n = nombre.lower()
    if tipo_bloque == "NFP_USD":
        if "nonfarm payrolls" in n and "private" not in n: return 5
        if "unemployment rate" in n: return 3
        if "average hourly earnings" in n: return 2
        if "private nonfarm payrolls" in n: return 2
    if tipo_bloque == "CPI_USD":
        if "core cpi" in n: return 5
        if "cpi" in n: return 4
    if tipo_bloque == "CPI_GBP":
        if "core cpi" in n: return 4
        if "cpi" in n: return 4
    if tipo_bloque == "EMPLOYMENT_CAD":
        if "employment change" in n: return 4
        if "unemployment rate" in n: return 3
    return 1

def es_dominante(nombre, tipo_bloque=None):
    n = nombre.lower()
    if tipo_bloque == "NFP_USD":
        return "nonfarm payrolls" in n and "private" not in n
    if tipo_bloque == "CPI_USD":
        return "core cpi" in n
    if tipo_bloque == "EMPLOYMENT_CAD":
        return "employment change" in n
    return False