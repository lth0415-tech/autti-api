from io import BytesIO

from openpyxl import Workbook

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples"

# FastAPI API 업로드 테스트
def test_create_reconciliation_with_sample_files():
    confirmation_path = SAMPLES_DIR / "confirmation_sample.xlsx"
    statement_path = SAMPLES_DIR / "statement_sample.xlsx"

    with (
        confirmation_path.open("rb") as confirmation_file,
        statement_path.open("rb") as statement_file,
    ):
        response = client.post(
            "/api/v1/reconciliations",
            files={
                "confirmation_file": (
                    "confirmation_sample.xlsx",
                    confirmation_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                "statement_file": (
                    "statement_sample.xlsx",
                    statement_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["batch_id"] is not None
    assert data["total_count"] == 4
    assert data["matched_count"] == 2
    assert data["mismatched_count"] == 1
    assert data["missing_count"] == 1
    assert data["duplicated_count"] == 0
    assert data["invalid_count"] == 0

# 결과 Excel 다운로드 API 테스트
def test_download_reconciliation_result_excel():
    confirmation_path = SAMPLES_DIR / "confirmation_sample.xlsx"
    statement_path = SAMPLES_DIR / "statement_sample.xlsx"

    with (
        confirmation_path.open("rb") as confirmation_file,
        statement_path.open("rb") as statement_file,
    ):
        create_response = client.post(
            "/api/v1/reconciliations",
            files={
                "confirmation_file": (
                    "confirmation_sample.xlsx",
                    confirmation_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                "statement_file": (
                    "statement_sample.xlsx",
                    statement_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
            },
        )

    assert create_response.status_code == 201

    batch_id = create_response.json()["batch_id"]

    download_response = client.get(
        f"/api/v1/reconciliations/{batch_id}/download"
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(download_response.content) > 0

# 잘못된 Excel 업로드에 대한 검증 테스트
# 1테스트용 Excel 생성
def make_excel_file(headers: list[str], rows: list[list]) -> BytesIO:
    workbook = Workbook()
    sheet = workbook.active

    sheet.append(headers)

    for row in rows:
        sheet.append(row)

    file = BytesIO()
    workbook.save(file)
    file.seek(0)

    return file
# 2잘못된 조회서 업로드 테스트
def test_create_reconciliation_returns_400_when_confirmation_required_column_missing():
    invalid_confirmation_file = make_excel_file(
        headers=[
            "confirmation_amount",
            "item_type",
            "institution_name",
            "currency",
            "base_date",
        ],
        rows=[
            [1000000, "DEPOSIT", "국민은행", "KRW", "2026-12-31"],
        ],
    )

    valid_statement_file = make_excel_file(
        headers=[
            "item_identifier",
            "book_amount",
            "item_type",
            "institution_name",
            "currency",
            "base_date",
        ],
        rows=[
            ["100123456", 1000000, "DEPOSIT", "국민은행", "KRW", "2026-12-31"],
        ],
    )

    response = client.post(
        "/api/v1/reconciliations",
        files={
            "confirmation_file": (
                "invalid_confirmation.xlsx",
                invalid_confirmation_file,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            "statement_file": (
                "statement.xlsx",
                valid_statement_file,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        },
    )

    assert response.status_code == 400