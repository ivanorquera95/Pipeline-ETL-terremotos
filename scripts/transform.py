import pandas as pd
import json
import glob
import os

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIRECTORIO_DATA = os.path.join(DIRECTORIO_SCRIPT, "..", "data")

def encontrar_archivo_mas_reciente():
    patron = os.path.join(DIRECTORIO_DATA, "raw_terremotos_*.json")
    archivos = glob.glob(patron)

    if not archivos:
        raise FileNotFoundError(
            f"No se encontró ningún archivo raw_terremotos_*.json en {DIRECTORIO_DATA}. "
            "Corré primero extract.py"
        )

    archivo_mas_reciente = max(archivos, key=os.path.getctime)
    print(f"Archivo encontrado: {archivo_mas_reciente}")
    return archivo_mas_reciente


def cargar_datos_crudos(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos


def extraer_campos_relevantes(datos_crudos):
    terremotos = []

    for feature in datos_crudos["features"]:
        propiedades = feature["properties"]
        coordenadas = feature["geometry"]["coordinates"]

        terremoto = {
            "magnitud": propiedades.get("mag"),
            "lugar": propiedades.get("place"),
            "fecha_timestamp_ms": propiedades.get("time"),
            "alerta_tsunami": propiedades.get("tsunami"),
            "longitud": coordenadas[0],
            "latitud": coordenadas[1],
            "profundidad_km": coordenadas[2],
        }
        terremotos.append(terremoto)

    print(f"Se extrajeron {len(terremotos)} registros.")
    return terremotos


def limpiar_datos(lista_terremotos):
    df = pd.DataFrame(lista_terremotos)

    df["fecha"] = pd.to_datetime(df["fecha_timestamp_ms"], unit="ms")
    df = df.drop(columns=["fecha_timestamp_ms"])

    filas_antes = len(df)
    df = df.dropna(subset=["magnitud"])
    filas_despues = len(df)
    if filas_antes != filas_despues:
        print(f"Se descartaron {filas_antes - filas_despues} filas sin magnitud.")

    df["alerta_tsunami"] = df["alerta_tsunami"].fillna(0)

    df["magnitud"] = df["magnitud"].astype(float)
    df["latitud"] = df["latitud"].astype(float)
    df["longitud"] = df["longitud"].astype(float)
    df["profundidad_km"] = df["profundidad_km"].astype(float)
    df["alerta_tsunami"] = df["alerta_tsunami"].astype(int)

    df = df.drop_duplicates()

    return df


def guardar_datos_limpios(df):
    os.makedirs(DIRECTORIO_DATA, exist_ok=True)
    nombre_archivo = os.path.join(DIRECTORIO_DATA, "terremotos_limpios.csv")
    df.to_csv(nombre_archivo, index=False, encoding="utf-8")
    print(f"Datos limpios guardados en: {nombre_archivo}")
    print(f"Total de registros: {len(df)}")
    return nombre_archivo


if __name__ == "__main__":
    ruta = encontrar_archivo_mas_reciente()
    datos_crudos = cargar_datos_crudos(ruta)
    terremotos = extraer_campos_relevantes(datos_crudos)
    df_limpio = limpiar_datos(terremotos)
    guardar_datos_limpios(df_limpio)

    print("\nPrimeras filas del resultado:")
    print(df_limpio.head())