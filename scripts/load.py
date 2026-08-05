import psycopg2
import pandas as pd
import os

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIRECTORIO_DATA = os.path.join(DIRECTORIO_SCRIPT, "..", "data")
RUTA_CSV_LIMPIO = os.path.join(DIRECTORIO_DATA, "terremotos_limpios.csv")

CONFIG_DB = {
    "host": os.environ.get("POSTGRES_DATA_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_DATA_PORT", "5433"),
    "dbname": "proyecto_datos_pipeline",
    "user": "ivan",
    "password": "pipeline34",
}

def conectar():
    conexion = psycopg2.connect(**CONFIG_DB)
    print("Conexión a PostgreSQL exitosa.")
    return conexion

def crear_tabla(conexion):
    query = """
    CREATE TABLE IF NOT EXISTS terremotos (
        id SERIAL PRIMARY KEY,
        magnitud FLOAT NOT NULL,
        lugar TEXT,
        alerta_tsunami INTEGER,
        longitud FLOAT,
        latitud FLOAT,
        profundidad_km FLOAT,
        fecha TIMESTAMP,
        fecha_carga TIMESTAMP DEFAULT NOW()
    );
    """
    cursor = conexion.cursor()
    cursor.execute(query)
    conexion.commit()
    cursor.close()
    print("Tabla 'terremotos' verificada/creada.")

def cargar_datos(conexion, ruta_csv):
    df = pd.read_csv(ruta_csv)

    cursor = conexion.cursor()

    query_insert = """
    INSERT INTO terremotos (magnitud, lugar, alerta_tsunami, longitud, latitud, profundidad_km, fecha)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    filas_insertadas = 0
    for _, fila in df.iterrows():
        valores = (
            fila["magnitud"],
            fila["lugar"],
            fila["alerta_tsunami"],
            fila["longitud"],
            fila["latitud"],
            fila["profundidad_km"],
            fila["fecha"],
        )
        cursor.execute(query_insert, valores)
        filas_insertadas += 1

    conexion.commit()
    cursor.close()
    print(f"Se insertaron {filas_insertadas} registros en la tabla 'terremotos'.")

if __name__ == "__main__":
    conexion = conectar()
    crear_tabla(conexion)
    cargar_datos(conexion, RUTA_CSV_LIMPIO)
    conexion.close()
    print("Conexión cerrada. Proceso de carga finalizado.")