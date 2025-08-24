# dags/sample_etl.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False
}

# Extract
def extract_data(**context):
    print(f"[Extract] Start")
    
    # 샘플 데이터
    sample_data = {
        'value1': 100,
        'value2': 200,
        'value3': 300
    }
    
    print(f"[Extract] data: {sample_data}")
    return sample_data

# Transform
def transform_data(**context):
    task_instance = context['task_instance']
    extracted_data = task_instance.xcom_pull(task_ids='extract_task')
    
    print("[Transform] Start")
    
    # value를 2배로 만드는 transform
    transformed_data = {
        'value1_modified': extracted_data['value1'] * 2,
        'value2_modified': extracted_data['value2'] * 2,
        'value3_modified': extracted_data['value3'] * 2
    }
    
    print(f"[Transform] data: {transformed_data}")
    return transformed_data

# Load
def load_data(**context):
    task_instance = context['task_instance']
    transformed_data = task_instance.xcom_pull(task_ids='transform_task')
    
    print("[Load] Start")
    print(f"[Load] data: {transformed_data}")
    return "ETL Process Completed"

with DAG(
    dag_id='sample_etl',
    default_args=default_args,
    description='Sample ETL Pipeline',
    schedule='@daily',  # @daily, @hourly, @weekly, @monthly, @yearly, ... Cron 표현식도 사용 가능
    start_date=datetime(2024, 1, 1),  # Dag를 실행하는 시점보다 이전이어야 함
    catchup=False,  # 이전 일정을 처리할지 여부 (False: 과거 일정 무시, True: 과거 일정 모두 실행)
                    # start_date부터 현재까지의 누락된 실행을 처리할지 결정하는 파라미터
                    # 프로덕션 환경에서는 일반적으로 False로 설정하여 과거 데이터 처리를 방지
    tags=['etl']
) as dag:

    extract_task = PythonOperator(
        task_id='extract_task',
        python_callable=extract_data
    )

    transform_task = PythonOperator(
        task_id='transform_task',
        python_callable=transform_data
    )

    load_task = PythonOperator(
        task_id='load_task',
        python_callable=load_data
    )

    # 태스크 순서
    extract_task >> transform_task >> load_task
