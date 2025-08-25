from airflow import DAG
import pendulum
import datetime
from airflow.operators.python import PythonOperator
import random


with DAG(
    dag_id="dags_python_operator",
    schedule="30 6 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="Asia/Seoul"),
    catchup=False,
    params={"example_key": "example_value"},
) as dag:
    def select_fruit():
        fruit_list = ['APPLE','BANANA', 'ORANGE', 'AVOCADO']
        rand_int = random.randint(0,3)
        print(fruit_list[rand_int])

    py_t1 = PythonOperator(
        task_id = 'py_t1',
        python_callable=select_fruit
    )

    py_t1
