# Autti

Autti는 금융기관조회서와 회사 제시 명세서를 비교하여 금액 일치 여부를 자동으로 검증하는 FastAPI 기반 대사 자동화 프로젝트입니다.

회계 감사 실무에서 금융기관조회서 PDF 또는 Excel 자료를 정리한 뒤, 회사 장부 명세서와 비교하는 과정을 웹/API 서비스 형태로 자동화하는 것을 목표로 합니다.

## 주요 기능

- 금융기관조회서 Excel 업로드
- 회사 제시 명세서 Excel 업로드
- 금융상품 식별자 기준 대사
- 금액 일치 여부 검증
- 대사 결과 DB 저장
- 대사 결과 Excel 다운로드
- Swagger API 문서 제공
- 간단한 웹 업로드 화면 제공
- pytest 기반 자동 테스트
- Docker 기반 로컬 실행
- AWS ECS Fargate 배포 가능

## 대사 기준

Autti는 특정 금융상품에만 종속되지 않도록 `item_identifier`를 기준 식별자로 사용합니다.

`item_identifier`는 다음과 같은 값을 포괄합니다.

- 예금 계좌번호
- 차입금 번호
- 보험 증권번호
- 보증 번호
- 계약 번호
- 기타 금융상품 고유 식별자

## 기술 스택

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- openpyxl
- Jinja2
- pytest
- Docker
- Docker Compose
- AWS ECR
- AWS ECS Fargate
- AWS RDS PostgreSQL
- AWS Application Load Balancer


## 프로젝트 구조

```text
app/
├── core/
│   ├── config.py
│   └── database.py
├── models/
│   └── reconciliation.py
├── repositories/
│   └── reconciliation_repository.py
├── routers/
│   ├── page_router.py
│   └── reconciliation_router.py
├── schemas/
│   └── reconciliation.py
├── services/
│   ├── excel_service.py
│   ├── reconciliation_logic.py
│   └── reconciliation_service.py
├── templates/
│   └── index.html
└── main.py

alembic/
docs/
samples/
tests/
```

## 계층구조

Autti는 Java Spring Boot의 Controller-Service-Repository 구조와 비슷하게 구성되어 있습니다.
Router
  HTTP 요청/응답 처리

Service
  비즈니스 흐름 처리

Repository
  DB 저장/조회 처리

Model
  DB 테이블 구조 정의

Schema
  API 요청/응답 데이터 구조 정의


## 실행 방법
## 로컬 실행
1. 가상환경 활성화
.venv\Scripts\Activate.ps1
2. 패키지 설치
개발 및 테스트용:
pip install -r requirements-dev.txt
운영 실행용:
pip install -r requirements.txt
3. 환경 변수 설정
.env.example을 참고하여 .env 파일을 생성합니다.
APP_NAME=Autti
ENV=local
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/autti
실제 DB 비밀번호는 Git에 올리지 않습니다.
4. DB 마이그레이션
python -m alembic upgrade head
5. 서버 실행
uvicorn app.main:app --reload
접속 주소:
http://127.0.0.1:8000
Swagger 문서:
http://127.0.0.1:8000/docs
헬스 체크:
http://127.0.0.1:8000/health

## Docker 로컬 실행
Docker Compose로 FastAPI와 PostgreSQL을 함께 실행할 수 있습니다.
docker compose up --build
DB 마이그레이션:
docker compose exec web alembic upgrade head
서비스 접속:
http://127.0.0.1:8000
종료:
docker compose down

## 테스트 실행
pytest
현재 테스트 범위:
대사 로직 단위 테스트
Excel 업로드 API 테스트
결과 Excel 다운로드 테스트
필수 컬럼 누락 검증 테스트
현재 구현 범위
현재 MVP에서는 Excel 기반 대사 자동화를 구현했습니다.
Excel 업로드
↓
필수 컬럼 검증
↓
item_identifier 정규화
↓
조회서 금액과 장부 금액 비교
↓
결과 DB 저장
↓
결과 Excel 다운로드


## AWS 배포 구조
Autti는 AWS ECS Fargate 기반으로 배포할 수 있습니다.
사용자 브라우저
→ Application Load Balancer
→ ECS Fargate
→ FastAPI Docker 컨테이너
→ RDS PostgreSQL
사용한 AWS 서비스:
Amazon ECR
Amazon ECS Fargate
Amazon RDS PostgreSQL
Application Load Balancer
CloudWatch Logs

AWS 배포 요약
1. Docker 이미지 빌드
2. ECR 리포지토리 생성
3. ECR에 Docker 이미지 push
4. RDS PostgreSQL 생성
5. Alembic으로 RDS 테이블 생성
6. ECS Task Definition 생성
7. ECS Fargate Service 생성
8. ALB 연결
9. 보안 그룹 설정
10. 웹 접속 및 기능 테스트

AWS 운영 환경 변수
ECS Task Definition에는 다음 환경 변수가 필요합니다.
APP_NAME=Autti
ENV=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@RDS_ENDPOINT:5432/DB_NAME
주의:
실제 DB 비밀번호는 README, GitHub, 코드에 올리지 않습니다.
운영 환경에서는 AWS Secrets Manager 또는 Parameter Store 사용을 고려합니다.

AWS 보안 그룹 구조
권장 흐름:
브라우저
→ ALB 80번 포트
→ ECS 8000번 포트
→ RDS 5432번 포트
권장 규칙:
ALB 보안 그룹
- Inbound: HTTP 80, Source 0.0.0.0/0

ECS 보안 그룹
- Inbound: TCP 8000, Source ALB 보안 그룹

RDS 보안 그룹
- Inbound: PostgreSQL 5432, Source ECS 보안 그룹

