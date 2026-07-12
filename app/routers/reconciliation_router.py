from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.reconciliation_repository import ReconciliationRepository
from app.schemas.reconciliation import (
    ReconciliationBatchResponse,
    ReconciliationExecuteResponse,
    ReconciliationResultResponse,
)
from app.services.reconciliation_service import ReconciliationService


router = APIRouter()


def get_reconciliation_service(
    db: Session = Depends(get_db),
) -> ReconciliationService:
    repository = ReconciliationRepository(db)
    return ReconciliationService(repository)


@router.post(
    "",
    response_model=ReconciliationExecuteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def execute_reconciliation(
    confirmation_file: UploadFile = File(...),
    statement_file: UploadFile = File(...),
    service: ReconciliationService = Depends(get_reconciliation_service),
):
    try:
        return await service.execute_reconciliation(
            confirmation_file=confirmation_file,
            statement_file=statement_file,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{batch_id}",
    response_model=ReconciliationBatchResponse,
)
def get_reconciliation_batch(
    batch_id: int,
    service: ReconciliationService = Depends(get_reconciliation_service),
):
    batch = service.get_batch(batch_id)

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대사 작업을 찾을 수 없습니다.",
        )

    return batch


@router.get(
    "/{batch_id}/results",
    response_model=list[ReconciliationResultResponse],
)
def get_reconciliation_results(
    batch_id: int,
    service: ReconciliationService = Depends(get_reconciliation_service),
):
    batch = service.get_batch(batch_id)

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대사 작업을 찾을 수 없습니다.",
        )

    return service.get_results(batch_id)


@router.get("/{batch_id}/download")
def download_reconciliation_result(
    batch_id: int,
    service: ReconciliationService = Depends(get_reconciliation_service),
):
    result = service.create_result_excel(batch_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대사 작업을 찾을 수 없습니다.",
        )

    filename, output = result

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )