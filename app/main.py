from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.routers.reconciliation_router import router as reconciliation_router
from app.routers.page_router import router as page_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic이 DB 테이블 생성을 담당.
    # 나중에 서버 시작/종료 시 필요한 작업이 생기면 추가.
    yield

app = FastAPI(
    title=settings.app_name,
    description="Autti - FastAPI 기반 금융기관조회서 대사 자동화 웹/API 서비스",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {
        "status":"ok",
        "env": settings.env,
    }

app.include_router(page_router)

app.include_router(
    reconciliation_router,
    prefix="/api/v1/reconciliations",
    tags=["reconciliations"],
)
