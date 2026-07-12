from app.services.reconciliation_logic import ReconciliationLogic


def test_reconcile_returns_matched_result():
    logic = ReconciliationLogic()

    confirmation_rows = [
        {
            "item_identifier": "100-123-456",
            "confirmation_amount": 1000000,
            "item_type": "DEPOSIT",
            "institution_name": "국민은행",
            "currency": "KRW",
            "base_date": "2026-12-31",
        }
    ]

    statement_rows = [
        {
            "item_identifier": "100123456",
            "book_amount": 1000000,
            "item_type": "DEPOSIT",
            "institution_name": "국민은행",
            "currency": "KRW",
            "base_date": "2026-12-31",
        }
    ]

    results = logic.reconcile(confirmation_rows, statement_rows)

    assert len(results) == 1
    assert results[0]["result_type"] == "MATCHED"
    assert results[0]["is_matched"] is True
    assert results[0]["difference_amount"] == 0


def test_reconcile_returns_amount_mismatch_result():
    logic = ReconciliationLogic()

    confirmation_rows = [
        {
            "item_identifier": "200-456-789",
            "confirmation_amount": 2000000,
            "item_type": "DEPOSIT",
            "institution_name": "신한은행",
            "currency": "KRW",
            "base_date": "2026-12-31",
        }
    ]

    statement_rows = [
        {
            "item_identifier": "200456789",
            "book_amount": 1900000,
            "item_type": "DEPOSIT",
            "institution_name": "신한은행",
            "currency": "KRW",
            "base_date": "2026-12-31",
        }
    ]

    results = logic.reconcile(confirmation_rows, statement_rows)

    assert len(results) == 1
    assert results[0]["result_type"] == "AMOUNT_MISMATCH"
    assert results[0]["is_matched"] is False
    assert results[0]["difference_amount"] == 100000


def test_reconcile_returns_missing_in_statement_result():
    logic = ReconciliationLogic()

    confirmation_rows = [
        {
            "item_identifier": "POL-999-001",
            "confirmation_amount": 3000000,
            "item_type": "INSURANCE",
            "institution_name": "삼성생명",
            "currency": "KRW",
            "base_date": "2026-12-31",
        }
    ]

    statement_rows = []

    results = logic.reconcile(confirmation_rows, statement_rows)

    assert len(results) == 1
    assert results[0]["result_type"] == "MISSING_IN_STATEMENT"
    assert results[0]["is_matched"] is False
    assert results[0]["book_amount"] is None