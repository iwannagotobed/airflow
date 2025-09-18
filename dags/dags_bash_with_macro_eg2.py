from airflow import DAG
import pendulum
from airflow.operators.bash import BashOperator

with DAG(
    dag_id = 'dags_bash_with_marco_eg2',
    schedule = '10 0 # * 6#2 ',
    start_date = pendulum.datetime(2023, 3, 1, tz= 'Asia/Seoul'),
    catchup = False
) as dag:
    
    # START_DATE: 전월 말일, END_DATE: 1일 전
    bash_task_1 = BashOperator(
        task_id = 'bash_task_2',
        env ={'START_DATE': '{{(data_interval_end.in_timezone("Asia/Seoul") - macros.dateutill.relativedelta.relativedelta(days=19)) | ds}}',
              'END_DATE': '{{(data_interval_end.in_timezone("Asia/Seoul") - macros.dateutill.relativedelta.relativedelta(days=14)) | ds}}'      
        },
        bash_command = 'echo "START_DATE: $START_DATE" && echo "END_DATE: $END_DATE"'
    )