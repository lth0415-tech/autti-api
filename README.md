# Autti

Autti는 금융기관조회서와 회사 제시 명세서를 비교하여 금액 일치 여부를 자동으로 검증하는 FastAPI 기반 대사 자동화 프로젝트입니다.

회계 감사 실무에서 금융기관조회서 PDF 또는 Excel 자료를 정리한 뒤, 회사 장부 명세서와 비교하는 과정을 웹/API 서비스 형태로 자동화하는 것을 목표로 합니다.

## 📌주요 기능

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

## 🔍대사 기준

Autti는 특정 금융상품에만 종속되지 않도록 `item_identifier`를 기준 식별자로 사용합니다.

`item_identifier`는 다음과 같은 값을 포괄합니다.

- 예금 계좌번호
- 차입금 번호
- 보험 증권번호
- 보증 번호
- 계약 번호
- 기타 금융상품 고유 식별자

## 🛠기술 스택

**백엔드**: Python, FastAPI, SQLAlchemy, Pydantic  
**화면**: Jinja2, HTML, JavaScript  
**DB**: PostgreSQL, AWS RDS PostgreSQL
**마이그레이션**: Alembic  
**Excel 처리**: openpyxl  
**인프라/배포**: Docker, Docker Compose, AWS ECR, AWS ECS Fargate, AWS Application Load Balancer  
**테스트**: pytest, FastAPI TestClient

## 🚀배포

**서비스 주소**: `http://autti-alb-1328064303.ap-northeast-2.elb.amazonaws.com`  (AWS ALB DNS를 통해 배포 테스트 완료) (비용 문제로 서비스 중지상태) 

**애플리케이션**: FastAPI 기반 웹 화면과 REST API를 하나의 Docker 컨테이너로 실행

**배포 흐름**: Docker 이미지 빌드 → Amazon ECR push → ECS Fargate 서비스 실행 → ALB 연결

**인프라**: AWS ECR · ECS Fargate · Application Load Balancer · RDS PostgreSQL

**DB 관리**: Alembic을 사용해 RDS PostgreSQL에 마이그레이션 적용

**로그**: CloudWatch Logs에서 ECS 컨테이너 실행 로그 및 오류 확인

**보안 그룹**: ALB는 HTTP 80 포트를 외부에 공개하고, ECS는 애플리케이션 포트 8000, RDS는 PostgreSQL 포트 5432를 필요한 경로에 맞게 허용

## 📁프로젝트 구조

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


## 💻실행 방법
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

