from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimopleHttpOperator
from airflow.decorators import task

with DAG(
    dag_id ='dags_simple_http_operator',
    start_date= pendulum.datetime(2023, 4, 1, tz='Asia/Seoul'),
    schedule=None,
    catchup=False
) as dag:
    

    ''' 서울시 공공자전거 대여소 정보'''
    tb_cycle_station_info = SimopleHttpOperator(
        task_id='tb_cycle_station_info',
        http_conn_id='openai.seoul.go.kr',
        endpoint='{{var.value.api_key_openai_seoul_go_kr}}/json/tbCyclestationInfo/1/10',
        method='GET',
        headers={'Content-Type': 'application/json',
                 'charset': 'utf-8',
                 'Accept':}
    )
