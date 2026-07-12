from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

# API 요청/응답 데이터 구조
class ReconciliationExecuteResponse(BaseModel):
    batch_id: int
    status: str
    total_count: int
    matched_count: int
    mismatched_count: int
    missing_count: int
    duplicated_count: int
    invalid_count: int
    download_url: str


class ReconciliationBatchResponse(BaseModel):
    id: int
    confirmation_file_name: str
    statement_file_name: str
    status: str
    total_count: int
    matched_count: int
    mismatched_count: int
    missing_count: int
    duplicated_count: int
    invalid_count: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ReconciliationResultResponse(BaseModel):
    id: int
    batch_id: int
    row_number: int | None
    item_identifier: str | None
    normalized_identifier: str
    item_type: str | None
    institution_name: str | None
    currency: str | None
    base_date: date | None
    confirmation_amount: Decimal | None
    book_amount: Decimal | None
    difference_amount: Decimal | None
    is_matched: bool
    result_type: str
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)