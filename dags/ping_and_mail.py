# -*- coding: utf-8 -*-
from __future__ import annotations
from datetime import datetime, timedelta
import json
import os
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator  # ← 코어 오퍼레이터로 교체

API_URL = os.getenv("FASTAPI_URL", "http://host.docker.internal:8000/")

def ping_fastapi() -> dict:
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"요청을 보냅니다! {sent_at}")
    print(f"GET {API_URL}")

    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()

    try:
        body = resp.json()
        body_for_log = json.dumps(body, ensure_ascii=False)
        body_str = json.dumps(body, ensure_ascii=False)  # Jinja 필터 미존재 대비
    except ValueError:
        body = resp.text
        body_for_log = body
        body_str = body

    print(f"결과: {resp.status_code} {resp.reason}")
    print(f"응답 본문: {body_for_log}")

    return {
        "sent_at": sent_at,
        "status": f"{resp.status_code} {resp.reason}",
        "url": API_URL,
        "body": body,        # 원본(딕트/문자열)
        "body_str": body_str # 항상 문자열 (이메일 본문용 안전빵)
    }

default_args = {
    "owner": "sunn",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}

with DAG(
    dag_id="ping_and_mail_every_minute",
    description="Ping local FastAPI and email the result on success",
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["exercise", "email", "api"],
) as dag:

    ping = PythonOperator(
        task_id="ping_root",
        python_callable=ping_fastapi,
        execution_timeout=timedelta(seconds=20),
    )

    email_ok = EmailOperator(
        task_id="email_success",
        to=["us990704@yonsei.ac.kr"],
        from_email="us990704@naver.com",   # ← SMTP 계정과 동일 권장
        subject="[OK] FastAPI 응답 {{ ts }}",
        html_content="""
        {% set r = ti.xcom_pull(task_ids='ping_root') %}
        <h3>FastAPI 요청 성공 ✅</h3>
        <ul>
          <li><b>요청 URL</b>: {{ r['url'] }}</li>
          <li><b>요청 시각</b>: {{ r['sent_at'] }}</li>
          <li><b>상태</b>: {{ r['status'] }}</li>
        </ul>

        {# 환경에 따라 tojson 필터가 없을 수 있어 안전하게 문자열도 함께 출력 #}
        <h4>응답 본문 (string)</h4>
        <pre style="white-space:pre-wrap">{{ r['body_str'] }}</pre>

        <h4>응답 본문 (json 시도)</h4>
        {% if r['body'] is mapping or r['body'] is sequence %}
          <pre style="white-space:pre-wrap">{{ r['body'] | tojson }}</pre>
        {% else %}
          <pre style="white-space:pre-wrap">{{ r['body'] }}</pre>
        {% endif %}
        """,
    )

    ping >> email_ok
