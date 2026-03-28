# =====================================================
# BLOQUE_MACRO.PY - DICCIONARIO DE DETECCIÓN ESTANDARIZADO
# =====================================================

BLOQUES = {

    # =========================
    # USD - ESTADOS UNIDOS
    # =========================

    "NFP_USD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "crecimiento",
        "confianza": "alta",
        "nucleo": [
            "Nonfarm Payrolls",
            "Unemployment Rate",
            "Average Hourly Earnings"
        ],
        "secundario": [
            "Participation Rate",
            "Average Weekly Hours",
            "Private Nonfarm Payrolls",
            "Manufacturing Payrolls",
            "U6 Unemployment Rate"
        ]
    },

    "CPI_USD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "inflacion",
        "confianza": "media",
        "nucleo": ["CPI", "Core CPI"],
        "secundario": ["CPI", "Core CPI"]
    },

    "PCE_USD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "inflacion",
        "confianza": "media",
        "nucleo": ["Core PCE Price Index"],
        "secundario": [
            "PCE Price Index",
            "Personal Income",
            "Personal Spending"
        ]
    },

    "FED_RATES_USD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "tasas",
        "confianza": "media-baja",
        "nucleo": ["Fed Interest Rate Decision"],
        "secundario": []
    },

    "ISM_MANUFACTURING_USD": {
        "relevancia_bloque": "CONDICIONAL",
        "confianza": "baja",
        "nucleo": ["ISM Manufacturing PMI"],
        "secundario": [
            "ISM Manufacturing Employment",
            "ISM Manufacturing Prices"
        ]
    },

    "ISM_SERVICES_USD": {
        "relevancia_bloque": "CONDICIONAL",
        "confianza": "baja",
        "nucleo": ["ISM Non-Manufacturing PMI"],
        "secundario": [
            "ISM Non-Manufacturing Employment",
            "ISM Non-Manufacturing Prices"
        ]
    },

    "PHILLY_FED_USD": {
        "relevancia_bloque": "CONDICIONAL",
        "confianza": "baja",
        "nucleo": ["Philly Fed Manufacturing Index"],
        "secundario": []
    },

    # =========================
    # CAD - CANADÁ
    # =========================

    "EMPLOYMENT_CAD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "crecimiento",
        "confianza": "media",
        "nucleo": [
            "Employment Change",
            "Unemployment Rate"
        ],
        "secundario": [
            "Full Employment Change",
            "Part Time Employment Change"
        ]
    },

    "CPI_CAD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "inflacion",
        "confianza": "media",
        "nucleo": ["CPI", "Core CPI"],
        "secundario": []
    },

    "BOC_RATES_CAD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "tasas",
        "confianza": "media-baja",
        "nucleo": ["BoC Interest Rate Decision"],
        "secundario": []
    },

    "GDP_CAD": {
        "relevancia_bloque": "CONDICIONAL",
        "tipo_base": "crecimiento",
        "confianza": "baja",
        "nucleo": ["GDP"],
        "secundario": []
    },

    # =========================
    # EUR - EUROZONA
    # =========================

    "CPI_EUR": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "inflacion",
        "confianza": "baja",  # 🔥 importante
        "nucleo": ["CPI", "Core CPI"],
        "secundario": []
    },

    "ECB_RATES_EUR": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "tasas",
        "confianza": "media-baja",
        "nucleo": ["ECB Interest Rate Decision"],
        "secundario": []
    },

    # =========================
    # GBP - REINO UNIDO
    # =========================

    "CPI_GBP": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "inflacion",
        "confianza": "media",  # 🔥 mejor que EUR
        "nucleo": ["CPI", "Core CPI"],
        "secundario": ["CPI"]
    },

    # =========================
    # AUD - AUSTRALIA
    # =========================

    "CPI_AUD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "inflacion",
        "confianza": "baja",
        "nucleo": ["CPI"],
        "secundario": ["CPI"]
    },

    "GDP_AUD": {
        "relevancia_bloque": "NUCLEO",
        "tipo_base": "crecimiento",
        "confianza": "baja",
        "nucleo": ["GDP"],
        "secundario": []
    },
}

CATEGORIAS_MAPA = {
    "NFP_USD": "Empleo",
    "EMPLOYMENT_CAD": "Empleo",
    "CPI_USD": "Inflación",
    "PCE_USD": "Inflación",
    "CPI_EUR": "Inflación",
    "CPI_CAD": "Inflación",
    "CPI_GBP": "Inflación",
    "CPI_AUD": "Inflación",
    "GDP_CAD": "Crecimiento",
    "GDP_AUD": "Crecimiento",
    "ISM_MANUFACTURING_USD": "Actividad Económica",
    "ISM_SERVICES_USD": "Actividad Económica",
    "PHILLY_FED_USD": "Actividad Económica",
    "FED_RATES_USD": "Bancos Centrales",
    "ECB_RATES_EUR": "Bancos Centrales",
    "BOC_RATES_CAD": "Bancos Centrales"
}