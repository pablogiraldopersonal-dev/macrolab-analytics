def obtener_tipo_evento(nombre):

    nombre = nombre.lower()

    # 🔵 EMPLEO (crecimiento)
    if "payroll" in nombre or "employment" in nombre:
        return "crecimiento"

    # 🔴 DESEMPLEO (invertido)
    if "unemployment" in nombre or "jobless" in nombre:
        return "inverso"

    # 🔴 INFLACIÓN
    if "cpi" in nombre or "pce" in nombre or "inflation" in nombre:
        return "inflacion"

    # 🟢 CRECIMIENTO ECONÓMICO
    if "gdp" in nombre:
        return "crecimiento"

    # 🟡 TASAS
    if "rate" in nombre:
        return "tasas"

    return "neutral"