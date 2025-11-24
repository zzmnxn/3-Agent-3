# 개요
여러 개로 분리된 고객 리뷰 pickle 데이터를 하나로 병합하고, 그 중 부정(Negative) 감정 리뷰만 추출하여 분석 리포트를 생성하는 AI Agent 시스템이다.
전체 흐름은 LangChain Tool Calling Agent기반으로 구성되어 있다.

## 폴더구조
```bash
try/
 ├── Dockerfile
 ├── docker-compose.yml
 ├── main.py
 ├── requirements.txt
 ├── styled_docx.py
 ├── tool/
 │    └── problem.py # 작성 파일
 └── data/
      ├── data1.pkl
      ├── data2.pkl
      ├── data3.pkl
```
## Try 실행 가이드
```bash

## 1. Build & Up
docker compose up --build -d
## 2. Exec
docker exec -it hateslop3_env bash

## 4. 내부 터미널에서 실행
python main.py
등 터미널 처럼 사용

## 5. 종료
docker compose down
```