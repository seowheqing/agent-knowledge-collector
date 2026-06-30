"""
Agent 知识库后端 - v3
FastAPI + SQLite + 通义千问AI解析 + 飞书多维表格同步 + 秒懂知识库推送

运行方式:
  1. 复制 .env.example 为 .env，填入你的密钥
  2. pip install fastapi uvicorn python-multipart PyPDF2 python-docx openpyxl httpx python-dotenv requests slowapi
  3. python main.py

访问: http://localhost:8000
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import DASHSCOPE_API_KEY, FEISHU_APP_ID, ALLOWED_ORIGINS
from database import init_db
from routes.api import router as api_router
from routes.pages import router as pages_router

# ===================== 初始化 =====================
init_db()

app = FastAPI(title="Agent知识库后端", version="3.0.0", docs_url=None, redoc_url=None)

# 速率限制
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== 注册路由 =====================
app.include_router(api_router)
app.include_router(pages_router)

# ===================== 启动 =====================
if __name__ == "__main__":
    print("=" * 50)
    print("  Agent 知识库后端 v3")
    print("=" * 50)
    print(f"  表单: http://localhost:8000/form")
    print(f"  后台: http://localhost:8000/admin")
    print("=" * 50)
    missing = []
    if not DASHSCOPE_API_KEY:
        missing.append("DASHSCOPE_API_KEY")
    if not FEISHU_APP_ID:
        missing.append("FEISHU_APP_ID")
    if missing:
        print(f"  ⚠️  未配置: {', '.join(missing)}（部分功能不可用）")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
