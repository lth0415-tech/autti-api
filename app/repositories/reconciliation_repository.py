from sqlalchemy.orm import Session, selectinload

from app.models.reconciliation import ReconciliationBatch, ReconciliationResult


class ReconciliationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_batch(self, batch: ReconciliationBatch) -> ReconciliationBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)

        return batch

    # reconciliation_batches 테이블에서 id가 batch_id인 작업을 조회.
    def find_batch_by_id(self, batch_id: int) -> ReconciliationBatch | None:
        return (
            self.db.query(ReconciliationBatch)
            .options(selectinload(ReconciliationBatch.results))
            .filter(ReconciliationBatch.id == batch_id)
            .first()
        )

    # reconciliation_results 테이블에서 특정 batch_id에 속한 상세 결과만 조회.
    def find_results_by_batch_id(self, batch_id: int) -> list[ReconciliationResult]:
        return (
            self.db.query(ReconciliationResult)
            .filter(ReconciliationResult.batch_id == batch_id)
            .order_by(ReconciliationResult.id.asc())
            .all()
        )