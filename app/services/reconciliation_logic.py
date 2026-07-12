from collections import Counter
from decimal import Decimal
from typing import Any

from app.services.excel_service import ExcelService

# 조회서 데이터와 회사 명세서 데이터를 실제로 비교하는 대사 로직.
# item_identifier 기준으로 매칭하고 금액 일치, 누락, 중복, 형식 오류를 판정.
class ReconciliationLogic:
    def __init__(self):
        self.excel_service = ExcelService()

    def reconcile(
        self,
        confirmation_rows: list[dict[str, Any]],
        statement_rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        statement_map = self._build_statement_map(statement_rows) # 회사 명세서 데이터를 XLOOKUP처럼 빠르게 찾을 수 있는 dict로 변환.
        confirmation_duplicates = self._find_duplicates(confirmation_rows) # 조회서와 회사 명세서 각각에서 중복된 대사 식별자를 미리 찾음.
        statement_duplicates = self._find_duplicates(statement_rows)

        results: list[dict[str, Any]] = []

        # 조회서 Excel의 각 행을 기준으로 회사 명세서와 대사.
        for confirmation_row in confirmation_rows:
            result = self._reconcile_one(
                confirmation_row=confirmation_row,
                statement_map=statement_map,
                confirmation_duplicates=confirmation_duplicates,
                statement_duplicates=statement_duplicates,
            )
            results.append(result)

        return results

    def _reconcile_one(
        self,
        confirmation_row: dict[str, Any],
        statement_map: dict[str, dict[str, Any]],
        confirmation_duplicates: set[str],
        statement_duplicates: set[str],
    ) -> dict[str, Any]:
        item_identifier = self._to_text(confirmation_row.get("item_identifier"))
        normalized_identifier = self.excel_service.normalize_identifier(item_identifier) # 하이픈/공백 차이를 제거한 비교용 식별자 생성.

        item_type = self._to_text(confirmation_row.get("item_type"))
        institution_name = self._to_text(confirmation_row.get("institution_name"))
        currency = self._to_text(confirmation_row.get("currency"))
        base_date = confirmation_row.get("base_date")

        confirmation_amount = self.excel_service.to_decimal(
            confirmation_row.get("confirmation_amount")
        )

        base_result = {
            "row_number": confirmation_row.get("row_number"),
            "item_identifier": item_identifier,
            "normalized_identifier": normalized_identifier,
            "item_type": item_type,
            "institution_name": institution_name,
            "currency": currency,
            "base_date": base_date,
            "confirmation_amount": confirmation_amount,
            "book_amount": None,
            "difference_amount": None,
            "is_matched": False,
            "result_type": None,
            "message": None,
        }

        if not normalized_identifier:
            return {
                **base_result,
                "result_type": "INVALID_DATA",
                "message": "대사 식별자가 비어 있습니다.",
            }

        if confirmation_amount is None:
            return {
                **base_result,
                "result_type": "INVALID_DATA",
                "message": "조회서 금액이 비어 있거나 숫자가 아닙니다.",
            }

        if normalized_identifier in confirmation_duplicates:
            return {
                **base_result,
                "result_type": "DUPLICATED_IN_CONFIRMATION",
                "message": "조회서 Excel 내 대사 식별자가 중복되었습니다.",
            }

        if normalized_identifier in statement_duplicates:
            return {
                **base_result,
                "result_type": "DUPLICATED_IN_STATEMENT",
                "message": "회사 명세서 Excel 내 대사 식별자가 중복되었습니다.",
            }

        statement_row = statement_map.get(normalized_identifier)

        if statement_row is None:
            return {
                **base_result,
                "result_type": "MISSING_IN_STATEMENT",
                "message": "회사 명세서에서 동일한 대사 식별자를 찾을 수 없습니다.",
            }

        book_amount = self.excel_service.to_decimal(statement_row.get("book_amount"))

        if book_amount is None:
            return {
                **base_result,
                "book_amount": None,
                "result_type": "INVALID_DATA",
                "message": "회사 명세서 금액이 비어 있거나 숫자가 아닙니다.",
            }

        difference_amount = confirmation_amount - book_amount
        is_matched = difference_amount == Decimal("0")

        if is_matched:
            result_type = "MATCHED"
            message = "일치"
        else:
            result_type = "AMOUNT_MISMATCH"
            message = "금액 불일치"

        return {
            **base_result,
            "book_amount": book_amount,
            "difference_amount": difference_amount,
            "is_matched": is_matched,
            "result_type": result_type,
            "message": message,
        }

    def _build_statement_map(
        self,
        statement_rows: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        statement_map: dict[str, dict[str, Any]] = {}

        for row in statement_rows:
            item_identifier = self._to_text(row.get("item_identifier"))
            normalized_identifier = self.excel_service.normalize_identifier(item_identifier)

            if normalized_identifier:
                statement_map[normalized_identifier] = row

        return statement_map

    def _find_duplicates(self, rows: list[dict[str, Any]]) -> set[str]:
        # 모든 행의 식별자를 정규화해서 비교 기준을 맞춤.
        identifiers = [
            self.excel_service.normalize_identifier(row.get("item_identifier"))
            for row in rows
        ]

        counter = Counter(
            identifier for identifier in identifiers
            if identifier
        )

        return {
            identifier for identifier, count in counter.items()
            if count > 1
        }

    @staticmethod
    def _to_text(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        if text == "":
            return None

        return text