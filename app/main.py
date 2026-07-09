from fastapi import FastAPI

app = FastAPI(
    title="Audit Automation API",
    description="FastAPI 기반 감사 조회서 자동화 API",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status":"ok"}