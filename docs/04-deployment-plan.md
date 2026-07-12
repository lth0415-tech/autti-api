
**docs/04-deployment-plan.md**
```markdown
# 배포 계획서

## 1. 문서 목적

이 문서는 금융기관조회서 대사 자동화 웹/API 서비스를 AWS 환경에 배포하기 위한 계획을 정의한다.

1차 목표는 FastAPI 애플리케이션을 AWS EC2에 배포하고, PostgreSQL DB를 사용하여 대사 결과를 저장하는 것이다.

## 2. 배포 목표

최종적으로 사용자는 웹 브라우저에서 서비스 URL에 접속하여 다음 기능을 사용할 수 있어야 한다.

- 조회서 Excel 업로드
- 회사 명세서 Excel 업로드
- 대사 실행
- 결과 요약 확인
- 결과 Excel 다운로드
- Swagger API 문서 확인

## 3. 로컬 개발 환경

로컬 개발 환경에서는 다음 구성을 사용한다.

```text
FastAPI
Uvicorn
PostgreSQL
SQLAlchemy
pytest