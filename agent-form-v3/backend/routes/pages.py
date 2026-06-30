"""
页面路由 - Landing page、表单页、管理后台
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from config import FRONTEND_DIR, BASE_DIR
from auth import verify_admin

router = APIRouter()

TEMPLATES_DIR = BASE_DIR / "templates"


@router.get("/form", response_class=HTMLResponse)
async def serve_form():
    p = FRONTEND_DIR / "index2.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h1>Not found</h1>", 404)


@router.get("/index2.html", response_class=HTMLResponse)
async def serve_form_alias():
    p = FRONTEND_DIR / "index2.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h1>Not found</h1>", 404)


@router.get("/", response_class=HTMLResponse)
async def serve_landing():
    p = FRONTEND_DIR / "landing.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h1>Not found</h1>", 404)


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(user: str = Depends(verify_admin)):
    """管理后台（需要密码）"""
    p = TEMPLATES_DIR / "admin.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h1>Not found</h1>", 404)
