from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime
from datetime import timedelta

import time

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': datetime(2019, 2, 25),
  'email': ['jdliauw@gmail.com'],
  'email_on_failure': False,
  'email_on_retry': True,
  'retries': 5,
  'retry_delay': timedelta(seconds=3),
}

dag = DAG(
  dag_id='my_dag', 
  description='Scrape yesterdays box score',
  'schedule_interval': '@daily',
  default_args=default_args)

func1 = PythonOperator(
  task_id='func1',
  python_callable=func1, 
  dag=dag)

func2 = PythonOperator(
  task_id='func2', 
  python_callable=func2, 
  dag=dag)

func3 = PythonOperator(
  task_id='func3', 
  python_callable=func3, 
  dag=dag)

# setting dependencies
func1 >> func3
func2 >> func3