"""create reconciliation tables

Revision ID: 194fd696f19b
Revises:
Create Date: 2026-07-12 13:47:40.217778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "194fd696f19b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reconciliation_batches",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("confirmation_file_name", sa.String(length=255), nullable=False),
        sa.Column("statement_file_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("matched_count", sa.Integer(), nullable=False),
        sa.Column("mismatched_count", sa.Integer(), nullable=False),
        sa.Column("missing_count", sa.Integer(), nullable=False),
        sa.Column("duplicated_count", sa.Integer(), nullable=False),
        sa.Column("invalid_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    

    op.create_table(
        "reconciliation_results",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("item_identifier", sa.String(length=255), nullable=True),
        sa.Column("normalized_identifier", sa.String(length=255), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=True),
        sa.Column("institution_name", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("base_date", sa.Date(), nullable=True),
        sa.Column("confirmation_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("book_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("difference_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("is_matched", sa.Boolean(), nullable=False),
        sa.Column("result_type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["reconciliation_batches.id"],
        ),
    )
    
    op.create_index(
        "ix_reconciliation_results_batch_id",
        "reconciliation_results",
        ["batch_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_reconciliation_results_batch_id",
        table_name="reconciliation_results",
    )
    op.drop_table("reconciliation_results")
    op.drop_table("reconciliation_batches")