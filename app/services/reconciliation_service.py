from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from typing import Any

from fastapi import UploadFile

from app.models.reconciliation import ReconciliationBatch, ReconciliationResult
from app.repositories.reconciliation_repository import ReconciliationRepository
from app.schemas.reconciliation import ReconciliationExecuteResponse
from app.services.excel_service import ExcelService
from app.services.reconciliation_logic import ReconciliationLogic


CONFIRMATION_REQUIRED_COLUMNS = [
    "item_identifier",
    "confirmation_amount",
]

STATEMENT_REQUIRED_COLUMNS = [
    "item_identifier",
    "book_amount",
]

# Autti 대사 업무의 전체 흐름을 조립하는 서비스.
# Excel 읽기, 대사 실행, DB 저장, 결과 조회, 결과 Excel 생성 과정을 연결.
class ReconciliationService:
    def __init__(self, repository: ReconciliationRepository):
        self.repository = repository

        # Excel 읽기/쓰기 담당 서비스
        self.excel_service = ExcelService()

        # 실제 대사 비교 로직 담당 클래스
        self.reconciliation_logic = ReconciliationLogic()

    async def execute_reconciliation(
        self,
        confirmation_file: UploadFile,
        statement_file: UploadFile,
    ) -> ReconciliationExecuteResponse:
        # 1. 조회서 Excel을 읽음.
        confirmation_rows = await self.excel_service.read_excel(
            confirmation_file,
            CONFIRMATION_REQUIRED_COLUMNS,
        )

        # 2. 회사 명세서 Excel을 읽음.
        statement_rows = await self.excel_service.read_excel(
            statement_file,
            STATEMENT_REQUIRED_COLUMNS,
        )

        # 3. 두 Excel 데이터를 대사.
        result_dicts = self.reconciliation_logic.reconcile(
            confirmation_rows=confirmation_rows,
            statement_rows=statement_rows,
        )

        # 4. 대사 결과를 종류별로 집계.
        counts = self._count_results(result_dicts)

        # 5. DB에 저장할 Batch 모델 생성.
        batch = ReconciliationBatch(
            confirmation_file_name=confirmation_file.filename or "confirmation.xlsx",
            statement_file_name=statement_file.filename or "statement.xlsx",
            status="COMPLETED",
            total_count=len(result_dicts),
            matched_count=counts["matched_count"],
            mismatched_count=counts["mismatched_count"],
            missing_count=counts["missing_count"],
            duplicated_count=counts["duplicated_count"],
            invalid_count=counts["invalid_count"],
            results=[
                self._to_result_model(result)
                for result in result_dicts
            ],
        )

        # 6. Repository를 통해 DB에 저장.
        saved_batch = self.repository.save_batch(batch)

        # 7. API 응답 DTO를 만들어 반환.
        return ReconciliationExecuteResponse(
            batch_id=saved_batch.id,
            status=saved_batch.status,
            total_count=saved_batch.total_count,
            matched_count=saved_batch.matched_count,
            mismatched_count=saved_batch.mismatched_count,
            missing_count=saved_batch.missing_count,
            duplicated_count=saved_batch.duplicated_count,
            invalid_count=saved_batch.invalid_count,
            download_url=f"/api/v1/reconciliations/{saved_batch.id}/download",
        )

    def get_batch(self, batch_id: int) -> ReconciliationBatch | None:
        # 특정 대사 작업 요약과 상세 결과를 조회.
        return self.repository.find_batch_by_id(batch_id)

    def get_results(self, batch_id: int) -> list[ReconciliationResult]:
        # 특정 대사 작업의 상세 결과만 조회.
        return self.repository.find_results_by_batch_id(batch_id)

    def create_result_excel(self, batch_id: int) -> tuple[str, BytesIO] | None:
        # 다운로드할 대사 결과를 DB에서 조회.
        batch = self.repository.find_batch_by_id(batch_id)

        if batch is None:
            return None

        result_dicts = [
            self._result_model_to_dict(result)
            for result in batch.results
        ]

        # ExcelService를 이용해 결과 Excel 파일을 메모리에 생성.
        output = self.excel_service.create_result_excel(result_dicts)

        filename = f"autti_reconciliation_result_{batch.id}.xlsx"

        return filename, output

    def _to_result_model(self, result: dict[str, Any]) -> ReconciliationResult:
        # 대사 로직의 dict 결과를 DB 모델 객체로 변환.
        return ReconciliationResult(
            row_number=result.get("row_number"),
            item_identifier=result.get("item_identifier"),
            normalized_identifier=result.get("normalized_identifier") or "",
            item_type=result.get("item_type"),
            institution_name=result.get("institution_name"),
            currency=result.get("currency"),
            base_date=self._to_date(result.get("base_date")),
            confirmation_amount=result.get("confirmation_amount"),
            book_amount=result.get("book_amount"),
            difference_amount=result.get("difference_amount"),
            is_matched=result.get("is_matched", False),
            result_type=result["result_type"],
            message=result.get("message"),
        )

    def _result_model_to_dict(self, result: ReconciliationResult) -> dict[str, Any]:
        # DB 모델 객체를 결과 Excel 생성에 필요한 dict로 변환.
        return {
            "item_identifier": result.item_identifier,
            "item_type": result.item_type,
            "institution_name": result.institution_name,
            "currency": result.currency,
            "base_date": result.base_date,
            "confirmation_amount": result.confirmation_amount,
            "book_amount": result.book_amount,
            "difference_amount": result.difference_amount,
            "is_matched": result.is_matched,
            "result_type": result.result_type,
            "message": result.message,
        }

    def _count_results(self, results: list[dict[str, Any]]) -> dict[str, int]:
        # result_type별로 집계.
        matched_count = 0
        mismatched_count = 0
        missing_count = 0
        duplicated_count = 0
        invalid_count = 0

        for result in results:
            result_type = result.get("result_type")

            if result_type == "MATCHED":
                matched_count += 1
            elif result_type == "AMOUNT_MISMATCH":
                mismatched_count += 1
            elif result_type == "MISSING_IN_STATEMENT":
                missing_count += 1
            elif result_type in {
                "DUPLICATED_IN_CONFIRMATION",
                "DUPLICATED_IN_STATEMENT",
            }:
                duplicated_count += 1
            elif result_type == "INVALID_DATA":
                invalid_count += 1

        return {
            "matched_count": matched_count,
            "mismatched_count": mismatched_count,
            "missing_count": missing_count,
            "duplicated_count": duplicated_count,
            "invalid_count": invalid_count,
        }

    @staticmethod
    def _to_date(value: Any) -> date | None:
        # Excel에서 날짜가 datetime으로 들어오면 date만 꺼냄.
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return None