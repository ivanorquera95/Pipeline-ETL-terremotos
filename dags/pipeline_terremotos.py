from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from extract import extraer_terremotos, guardar_datos_crudos
from transform import (
    encontrar_archivo_mas_reciente,
    cargar_datos_crudos,
    extraer_campos_relevantes,
    limpiar_datos,
    guardar_datos_limpios,
)
from load import conectar, crear_tabla, cargar_datos, RUTA_CSV_LIMPIO



def tarea_extract():
    datos = extraer_terremotos()
    guardar_datos_crudos(datos)

def tarea_transform():
    ruta = encontrar_archivo_mas_reciente()
    datos_crudos = cargar_datos_crudos(ruta)
    terremotos = extraer_campos_relevantes(datos_crudos)
    df_limpio = limpiar_datos(terremotos)
    guardar_datos_limpios(df_limpio)

def tarea_load():
    conexion = conectar()
    crear_tabla(conexion)
    cargar_datos(conexion, RUTA_CSV_LIMPIO)
    conexion.close()

default_args = {
    "owner": "ivan",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pipeline_terremotos",
    default_args=default_args,
    description="Pipeline ETL: extrae terremotos del USGS, los limpia y los carga a PostgreSQL",
    schedule_interval="@daily",
    start_date=datetime(2026, 8, 1),
    catchup=False,
    tags=["portfolio", "etl", "terremotos"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_terremotos",
        python_callable=tarea_extract,
    )

    transform_task = PythonOperator(
        task_id="transform_terremotos",
        python_callable=tarea_transform,
    )

    load_task = PythonOperator(
        task_id="load_terremotos",
        python_callable=tarea_load,
    )

    extract_task >> transform_task >> load_task