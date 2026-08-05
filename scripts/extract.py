import requests
import json
import os
from datetime import datetime, timedelta

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIRECTORIO_DATA = os.path.join(DIRECTORIO_SCRIPT, "..", "data")

def obtener_rango_fechas():
    fecha_fin = datetime.utcnow()
    fecha_inicio = fecha_fin - timedelta(days=1)
    return fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")

def extraer_terremotos():
    fecha_inicio, fecha_fin = obtener_rango_fechas()

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": fecha_inicio,
        "endtime": fecha_fin,
        "minmagnitude": 2.5
    }

    print(f"Consultando terremotos desde {fecha_inicio} hasta {fecha_fin}...")
    respuesta = requests.get(url, params=params)
    respuesta.raise_for_status()

    datos = respuesta.json()
    print(f"Se encontraron {len(datos['features'])} terremotos.")

    return datos


def guardar_datos_crudos(datos):
    os.makedirs(DIRECTORIO_DATA, exist_ok=True)
    nombre_archivo = os.path.join(
        DIRECTORIO_DATA,
        f"raw_terremotos_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2)

    print(f"Datos guardados en: {nombre_archivo}")
    return nombre_archivo


if __name__ == "__main__":
    datos = extraer_terremotos()
    guardar_datos_crudos(datos)