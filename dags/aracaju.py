from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

def etl_aracaju():
    CAMINHO_CSV = '/opt/airflow/dags/dados_processo_seletivo.csv'
    df = pd.read_csv(CAMINHO_CSV)
    df = df[df['city'].str.upper() == 'ARACAJU'].reset_index(drop=True)
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    pg_hook = PostgresHook(postgres_conn_id='postgres_terralab')
    engine = pg_hook.get_sqlalchemy_engine()
    
    df.to_sql(
        'enderecos_aracaju', 
        con=engine, 
        if_exists='replace',
        index=False
    )
    
with DAG(
    dag_id='processar_enderecos_aracaju',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    tarefa_etl = PythonOperator(
        task_id='filtrar_e_salvar_dados',
        python_callable=etl_aracaju
    )