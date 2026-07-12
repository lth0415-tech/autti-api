from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# DB 테이블 구조
class ReconciliationBatch(Base):
    __tablename__ = "reconciliation_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    confirmation_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    statement_file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")

    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mismatched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    results: Mapped[list["ReconciliationResult"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class ReconciliationResult(Base):
    __tablename__ = "reconciliation_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    batch_id: Mapped[int] = mapped_column(
        ForeignKey("reconciliation_batches.id"),
        nullable=False,
        index=True,
    )

    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    item_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_identifier: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    item_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    institution_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    base_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    confirmation_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    book_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    difference_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    is_matched: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    result_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    batch: Mapped[ReconciliationBatch] = relationship(
        back_populates="results",
    )