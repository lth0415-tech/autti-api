# 금융기관조회서 대사 자동화 웹/API 서비스 기획서

## 1. 프로젝트 개요

이 프로젝트는 FastAPI를 기반으로 금융기관조회서 회신 자료와 회사가 제시한 금융기관 관련 명세서를 대사하는 웹/API 서비스를 만드는 것을 목표로 한다.

사용자는 웹 화면에서 금융기관조회서 정리 Excel과 회사 제시 명세서 Excel을 업로드하고, 시스템은 계좌번호를 기준으로 두 파일의 데이터를 매칭하여 금액 및 주요 항목의 일치 여부를 자동으로 검증한다.

검증 결과는 웹 화면에서 요약으로 확인할 수 있으며, 상세 결과는 Excel 파일로 다운로드할 수 있다.

## 2. 프로젝트 목적

실무에서는 금융기관조회서를 PDF로 회신받은 뒤, 사람이 조회서 내용을 Excel로 옮기고, 회사가 제시한 명세서와 XLOOKUP 등의 Excel 기능을 이용해 금액 및 세부 항목을 비교한다.

이 과정은 반복적이고 수작업 오류가 발생하기 쉽다.

본 프로젝트는 이러한 대사 작업을 서비스화하여 다음을 달성하는 것을 목적으로 한다.

- 계좌번호 기준 매칭 자동화
- 조회서 금액과 회사 명세서 금액 비교 자동화
- 누락 계좌, 중복 계좌, 금액 불일치 탐지
- 대사 결과의 표준화
- 대사 이력의 DB 저장
- 결과 Excel 다운로드 제공
- 향후 AI/PDF 자동 추출 기능 확장 기반 마련

## 3. 핵심 기능

1차 MVP의 핵심 기능은 다음과 같다.

- 간단한 웹 화면 제공
- 금융기관조회서 정리 Excel 업로드
- 회사 제시 명세서 Excel 업로드
- 계좌번호 기준 데이터 매칭
- 조회서 금액과 회사 명세서 금액 비교
- 일치/불일치/누락/중복 결과 생성
- 대사 결과 PostgreSQL 저장
- 결과 Excel 다운로드
- Swagger API 문서 제공
- pytest 기반 테스트 작성

## 4. 기술 스택

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy

### Database

- PostgreSQL

### Template / Web

- FastAPI Templates
- HTML
- CSS

### Test

- pytest

### Deployment

- AWS EC2
- AWS RDS PostgreSQL
- Nginx
- Gunicorn 또는 Uvicorn

## 5. 설계 방향

본 프로젝트는 Java Spring Boot에서 학습한 Controller-Service-Repository 구조와 유사하게 계층을 분리한다.

FastAPI에서는 다음과 같은 구조로 설계한다.

| Spring Boot | FastAPI |
| --- | --- |
| Controller | Router |
| Service | Service |
| Repository | Repository |
| Entity | Model |
| DTO | Schema |
| application.yml | Config / Env |
| DB | PostgreSQL |

계층 분리의 목적은 다음과 같다.

- API 요청 처리와 업무 로직 분리
- 업무 로직과 DB 접근 로직 분리
- 테스트하기 쉬운 구조 확보
- 향후 AI/PDF 추출 기능 확장 용이
- AWS 배포 환경에서도 유지보수 가능한 구조 확보

## 6. 전체 업무 흐름

```mermaid
flowchart TD
    A[사용자 웹 접속] --> B[조회서 Excel 업로드]
    A --> C[회사 명세서 Excel 업로드]
    B --> D[대사 실행]
    C --> D
    D --> E[계좌번호 기준 매칭]
    E --> F[금액 및 주요 항목 비교]
    F --> G[일치/불일치/누락/중복 결과 생성]
    G --> H[PostgreSQL에 결과 저장]
    H --> I[웹 화면에 요약 표시]
    I --> J[결과 Excel 다운로드]