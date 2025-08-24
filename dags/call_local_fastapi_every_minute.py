# -*- coding: utf-8 -*-
"""
매 1분마다 http://host.docker.internal:8000/ 호출
Airflow 로그에 아래 순서로 남김:
- "요청을 보냅니다! {YYYY-mm-dd HH:MM:SS}"
- "GET {URL}"
- "결과: {STATUS_CODE} {REASON}"
- "응답 본문: {JSON or TEXT}"

Linux 도커에서 host.docker.internal 해석 안 되면 compose에:
  extra_hosts:
    - "host.docker.internal:host-gateway"
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

API_URL = os.getenv("FASTAPI_URL", "http://host.docker.internal:8000/")

def ping_fastapi() -> dict:
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ↓↓↓ Airflow 로그에 딱 떨어지게 남기는 출력 (stdout도 캡처됨)
    print(f"요청을 보냅니다! {sent_at}")
    print(f"GET {API_URL}")

    resp = requests.get(API_URL, timeout=10)
    status_line = f"{resp.status_code} {resp.reason}"
    print(f"결과: {status_line}")

    try:
        body = resp.json()
        body_log = json.dumps(body, ensure_ascii=False)
    except ValueError:
        body = resp.text
        body_log = body
    print(f"응답 본문: {body_log}")

    # 실패면 재시도를 위해 예외 발생
    resp.raise_for_status()

    # XCom으로도 남김(웹UI에서 확인 가능)
    return {"sent_at": sent_at, "status": status_line, "body": body}

default_args = {
    "owner": "sunn",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}

with DAG(
    dag_id="call_local_fastapi_every_minute",
    description="Ping local FastAPI and log cleanly every minute",
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["exercise", "local", "api"],
) as dag:
    call_api = PythonOperator(
        task_id="ping_root",
        python_callable=ping_fastapi,
        execution_timeout=timedelta(seconds=20),
    )

    call_api

