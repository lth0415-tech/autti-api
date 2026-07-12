# 데이터 모델 설계서

## 1. 문서 목적

이 문서는 금융기관조회서 대사 자동화 웹/API 서비스에서 사용할 PostgreSQL 데이터 모델을 정의한다.

본 프로젝트는 금융기관조회서 정리 Excel과 회사 제시 명세서 Excel을 업로드받아, 대사 식별자 기준으로 항목을 매칭하고 금액 및 주요 항목의 일치 여부를 검증한다.

검증 결과는 PostgreSQL에 저장되며, 사용자는 이후 대사 이력과 상세 결과를 조회하거나 결과 Excel을 다운로드할 수 있다.

## 2. 데이터 모델 개요

1차 MVP에서 사용하는 주요 테이블은 다음과 같다.

| 테이블명 | 설명 |
| --- | --- |
| reconciliation_batches | 대사 작업 단위 저장 |
| reconciliation_results | 항목별 대사 결과 저장 |

관계는 다음과 같다.

```text
reconciliation_batches 1 : N reconciliation_results