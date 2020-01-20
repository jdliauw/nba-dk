from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import box_score_scraper

# Following are defaults which can be overridden later on
default_args = {
    'owner': 'jdliauw',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 1),
    'email': ['jdliauw@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    dag_id='boxscore_pbp',
    default_args=default_args,
    schedule_interval='0 13  * * *')

t1 = PythonOperator(
    task_id='boxscore_pbp',
    python_callable=box_score_scraper.run,
    dag=dag)
