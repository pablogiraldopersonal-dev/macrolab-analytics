import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/"
}

def obtener_eventos_semana(fecha_inicio, fecha_fin):
    print("RANGO BUSCADO:", fecha_inicio, "→", fecha_fin)

    eventos = []

    # Modificación en investing_fetcher.py para búsqueda profunda
    for offset in [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]:
        try:
            payload = {
                "timeZone": "55",
                "timeFilter": "timeOnly",
                "currentTab": "custom",
                "dateFrom": fecha_inicio,
                "dateTo": fecha_fin,
                "limit_from": str(offset),
                "importance[]": ["2", "3"],
                "currency[]": ["5", "12", "4", "25", "6"]
            }

            response = requests.post(URL, headers=HEADERS, data=payload, timeout=15)
            
            if response.status_code != 200:
                print(f"Error en servidor: {response.status_code}")
                continue

            data = response.json()
            html = data.get("data", "")
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            filas = soup.select("tr.js-event-item")
            
            if not filas:
                break 

            print(f"OFFSET {offset} | FILAS RECIBIDAS: {len(filas)}")
            fecha_actual = fecha_inicio

            for fila in filas:
                if "theDay" in fila.get("class", []):
                    try:
                        texto = fila.get_text(strip=True)
                        texto += ", " + str(datetime.now().year)
                        fecha_actual = datetime.strptime(texto, "%A, %B %d, %Y").strftime("%Y-%m-%d")
                    except:
                        pass
                    continue

                if not fila.has_attr("id"):
                    continue

                impacto = len(fila.select("i.grayFullBullishIcon"))
                if impacto == 0:
                    impacto = len(fila.select("i.bullishIconFull"))

                cur = fila.find("td", class_="flagCur")
                divisa = cur.get_text(strip=True).upper() if cur else ""

                ev_td = fila.find("td", class_="event")
                nombre = ev_td.get_text(strip=True) if ev_td else ""
                
                ruido = ["speaks", "speech", "auction", "bond", "bill", "testimony"]
                if any(r in nombre.lower() for r in ruido):
                    continue

                try:
                    id_num = fila["id"].split("_")[1]
                except:
                    continue

                td_actual = fila.find("td", id=f"res_{id_num}") or fila.find("td", class_="act")
                forecast_td = fila.find("td", class_="fore")
                previous_td = fila.find("td", class_="prev")

                actual = td_actual.get_text(strip=True) if td_actual else ""
                forecast = forecast_td.get_text(strip=True) if forecast_td else ""
                previous = previous_td.get_text(strip=True) if previous_td else ""

                fecha_evento_raw = fila.get("data-event-datetime", "")
                if fecha_evento_raw:
                    try:
                        dt = datetime.strptime(fecha_evento_raw, "%Y/%m/%d %H:%M:%S")
                        dt_ajustado = dt - timedelta(hours=5)
                        fecha = dt_ajustado.strftime("%Y-%m-%d")
                        hora = dt_ajustado.strftime("%H:%M")
                    except Exception as e:
                        print(f"Error al convertir hora: {e}")
                        fecha, hora = fecha_actual, ""
                else:
                    fecha, hora = fecha_actual, ""

                eventos.append({
                    "fecha": fecha,
                    "hora": hora,
                    "divisa": divisa,
                    "nombre": nombre,
                    "actual": actual,
                    "forecast": forecast,
                    "previous": previous,
                    "impacto": impacto
                })

        except Exception as e:
            print(f"Error en offset {offset}: {e}")
            continue

    print("TOTAL EVENTOS FILTRADOS:", len(eventos))
    return eventos