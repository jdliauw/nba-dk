from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime
from datetime import timedelta

import time

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': datetime(2018, 9, 1),
  'email': ['jdliauw@gmail.com'],
  'email_on_failure': False,
  'email_on_retry': True,
  'retries': 1,
  'retry_delay': timedelta(seconds=3),
}

def func1():
  time.sleep(2.5)
  print("YO")

def func2():
  time.sleep(1.5)
  print("YOYO")

def func3():
  time.sleep(.5)
  print("YOYOYO")

dag = DAG(
  dag_id='my_dag', 
  description='Simple tutorial DAG',
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