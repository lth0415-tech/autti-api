from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

# HTML 파일들이 들어있는 폴더 위치를 FastAPI에 알려줌.
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def index_page(request: Request):
    """
    사용자가 브라우저로 접속했을 때 보여줄 첫 화면.
    """
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    )