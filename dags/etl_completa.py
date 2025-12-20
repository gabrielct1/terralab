from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pyogrio

def complete_etl():
    CAMINHO_CSV = '/opt/airflow/dags/dados_processo_seletivo.csv'
    CAMINHO_SHP = '/opt/airflow/dags/BR_UF_2024/BR_UF_2024.shp'
    
    df = pd.read_csv(CAMINHO_CSV).drop(columns='Unnamed: 0')
    ufs = pyogrio.read_dataframe(CAMINHO_SHP)
    ufs = ufs.to_crs("EPSG:4326")
    
    df = df[df['geoapi_id'].str.lower() != 'openrouteservice']
    
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    gdf_joined = gpd.sjoin(gdf_points, ufs, how='left', predicate='within')
    df_final = gdf_joined[gdf_joined['state'] == gdf_joined['SIGLA_UF']].copy()
    
    pg_hook = PostgresHook(postgres_conn_id='postgres_terralab')
    engine = pg_hook.get_sqlalchemy_engine()
    
    df_final = pd.DataFrame(df_final.drop(columns=['geometry', 'index_right']))
    
    df_final.to_sql(
        'dados_reais_tratados', 
        con=engine, 
        if_exists='replace',
        index=False
    )
    
with DAG(
    dag_id='processo_etl_completo_geopandas',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    tarefa_etl = PythonOperator(
        task_id='executar_etl_geografico',
        python_callable=complete_etl
    )